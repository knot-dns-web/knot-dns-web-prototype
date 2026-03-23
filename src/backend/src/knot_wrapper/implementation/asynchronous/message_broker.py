from enum import Enum

import asyncio
import redis.asyncio as redis

from pydantic import BaseModel
import uuid

from libknot.control import KnotCtl

from ...error.base_error import KnotError, KnotErrorData, KnotErrorType, KnotCtlError

from .task import DNSCommit, DNSTaskType, DNSCommitType

from ..base_operations.config import set_config, unset_config, begin_config, commit_config, abort_config
from ..base_operations.zone import set_zone, unset_zone, begin_zone, commit_zone, abort_zone, backup_zone, restore_zone, flush_zone

class Task(BaseModel):
    id: str
    commit: DNSCommit

class TaskResult(BaseModel):
    exception_text: str | None
    type: KnotErrorType | None
    data: KnotErrorData | None

class TaskError(Exception):
    pass

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

    def __apply_commit(self, commit: DNSCommit):
        ctl = KnotCtl()
        ctl.connect(self._socket_path)

        tasks = commit.tasks
        commit_type = commit.type
        zone_name = commit.zone_name

        is_conf = commit_type == DNSCommitType.conf
        is_committed = False

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
                commit_config(ctl)
            else:
                commit_zone(ctl, zone_name)
                flush_zone(ctl, zone_name)
            is_committed = True
        finally:
            if not is_committed:
                if is_conf:
                    abort_config(ctl)
                else:
                    abort_zone(ctl, zone_name)

    async def run(self):
        while True:
            exception_text = None
            error_type = None
            error_data = None
            try:
                result = await self._redis.brpop( # type: ignore
                    self._channel,
                    timeout=0
                )
                _, task_data = result
                task = Task.model_validate_json(task_data)
                commit = task.commit
                task_id = task.id

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
            raise TimeoutError("Task queue timed out")
        
        _, reply_data = reply
        result = TaskResult.model_validate_json(reply_data)
        exception_text = result.exception_text
        result_type = result.type
        result_data = result.data

        if exception_text:
            raise TaskError(exception_text)
        elif result_type is not None and result_data is not None:
            raise KnotError(result_type, result_data)
