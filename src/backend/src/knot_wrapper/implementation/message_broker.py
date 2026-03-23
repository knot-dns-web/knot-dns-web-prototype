from enum import Enum

import asyncio
import redis.asyncio as redis

from pydantic import BaseModel
import uuid

from libknot.control import KnotCtl

from ..error.base_error import KnotError, KnotErrorData, KnotErrorType, KnotCtlError

from .task import DNSCommit, DNSTaskType, DNSCommitType

from .base_operations.config import set_config, unset_config, begin_config, commit_config, abort_config
from .base_operations.zone import set_zone, unset_zone, begin_zone, commit_zone, abort_zone, backup_zone, restore_zone, status_zone

class Task(BaseModel):
    id: str
    commit: DNSCommit

class TaskResult(BaseModel):
    exception_text: str | None
    type: KnotErrorType | None
    data: KnotErrorData | None

class TaskError(Exception):
    pass

_global_configuration_version = 0
def get_configuration_version():
    global _global_configuration_version
    return _global_configuration_version

class VersionConflictError(Exception):
    def __init__(self, object: str, old_version: int | None, new_version: int | None) -> None:
        super().__init__()
        self.object = object
        self.old_version = old_version
        self.new_version = new_version

    def __str__(self) -> str:
        return f"Version of {self.object} had version {self.old_version} but already having version {self.new_version}"

class DNSWorker:
    def __init__(
        self,
        redis: redis.Redis,
        channel: str,
        socket_path: str
    ):
        self._redis = redis
        self._socket_path = socket_path
        self._channel = channel

    def __get_current_zone_versions(self, ctl: KnotCtl, zone_name: str | None):
        versions: dict[str, int | None] = {}
        serial_data = status_zone(ctl, zone_name, "+serial")
        for per_zone_name in serial_data: # can be many serials by zone_name "--" (None)
            values = serial_data[per_zone_name]
            serial = values['serial']
            if serial == '-':
                versions[per_zone_name] = None
            else:
                serial_int = int(serial)
                versions[per_zone_name] = serial_int
        return versions

    def __compare_zone_versions(
        self,
        object: str,
        old_versions: dict[str, int | None],
        new_versions: dict[str, int | None]
    ):
        for version_zone_name, new_version in new_versions.items():
            if version_zone_name not in old_versions:
                continue
            old_version = old_versions[version_zone_name]
            if (
                (new_version is None and old_version is None) or
                (new_version is not None and old_version is not None)
            ):
                continue
            
            if new_version is None or old_version is None or new_version < old_version: 
                raise VersionConflictError(object, old_version, new_version)

    def __apply_commit(self, commit: DNSCommit):
        global _global_configuration_version

        ctl = KnotCtl()
        ctl.connect(self._socket_path)

        tasks = commit.tasks
        commit_type = commit.type
        zone_name = commit.zone_name

        is_conf = commit_type == DNSCommitType.conf
        is_committed = False

        abort_config(ctl)
        abort_zone(ctl)
        if is_conf:
            begin_config(ctl)
        else:
            begin_zone(ctl, zone_name)
        try:
            for task in tasks:
                match task.type:
                    case DNSTaskType.conf_set:
                        set_config(ctl, **task.data)
                    case DNSTaskType.conf_unset:
                        unset_config(ctl, **task.data)
                    case DNSTaskType.zone_set:
                        set_zone(ctl, **task.data)
                    case DNSTaskType.zone_unset:
                        unset_zone(ctl, **task.data)
                    case DNSTaskType.zone_backup:
                        backup_zone(ctl, **task.data)
                    case DNSTaskType.zone_restore:
                        restore_zone(ctl, **task.data)

            if is_conf:
                old_version = commit.versions[""]
                new_version = _global_configuration_version

                if old_version is None:
                    raise Exception

                if new_version < old_version: 
                    raise VersionConflictError(f"zone {zone_name}", old_version, new_version)
            else:
                old_versions = commit.versions
                new_versions = self.__get_current_zone_versions(ctl, zone_name)
                self.__compare_zone_versions(f"zone {zone_name}", old_versions, new_versions)

            is_committed = True
            if is_conf:
                _global_configuration_version += 1
                commit_config(ctl)
            else:
                commit_zone(ctl, zone_name)
        finally:
            if not is_committed:
                if is_conf:
                    abort_config(ctl)
                else:
                    abort_zone(ctl, zone_name)

    async def run(self):
        while True:
            result = await self._redis.brpop( # type: ignore
                self._channel,
                timeout=0
            )
            _, task_data = result
            task = Task.model_validate_json(task_data)
            commit = task.commit
            task_id = task.id

            exception_text = None
            error_type = None
            error_data = None

            try:
                self.__apply_commit(commit)
            except KnotCtlError as e:
                error = KnotError.from_raw_error(e)
                error_type = error.error_type
                error_data = error.data
            except Exception as e:
                exception_text = str(e)

            result = TaskResult(
                exception_text=exception_text,
                type=error_type,
                data=error_data
            )
            result_json = result.model_dump_json()
            await self._redis.lpush(task_id, result_json) # type: ignore

class DNSTaskProducer:
    def __init__(
        self,
        redis: redis.Redis,
        channel: str,
    ):
        self._redis = redis
        self._channel = channel

    async def enqueue_commit(self, commit: DNSCommit):
        task_id = str(uuid.uuid4())
        task = Task(
            id=task_id,
            commit = commit
        )
        task_json = task.model_dump_json()
        await self._redis.lpush(self._channel, task_json) # type: ignore

        try:
            reply = await self._redis.blpop( # type: ignore
                task_id,
                timeout=0,
            )

        except asyncio.CancelledError:
            await self._redis.delete(task_id)
            raise

        if reply is None:
            await self._redis.delete(task_id)
            raise TimeoutError("Message queue timed out")
        
        _, reply_data = reply
        result = TaskResult.model_validate_json(reply_data)
        exception_text = result.exception_text
        result_type = result.type
        result_data = result.data

        if exception_text:
            raise TaskError(exception_text)
        elif result_type is not None and result_data is not None:
            raise KnotError(result_type, result_data)
