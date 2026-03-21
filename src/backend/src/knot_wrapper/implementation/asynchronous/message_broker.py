
import asyncio
import redis.asyncio as redis

from libknot.control import KnotCtl

from .task import DNSCommit, DNSTaskType, DNSCommitType

from ..base_operations.config import set_config, unset_config, begin_config, commit_config, abort_config
from ..base_operations.zone import set_zone, unset_zone, begin_zone, commit_zone, abort_zone

class DNSWorker:
    def __init__(
        self,
        redis: redis.Redis,
        channel: str,
        socket_path: str
    ) -> None:
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
        is_commited = False

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
            if is_conf:
                commit_config(ctl)
            else:
                commit_zone(ctl, zone_name)
            is_commited = True
        finally:
            if not is_commited:
                if is_conf:
                    abort_config(ctl)
                else:
                    abort_zone(ctl, zone_name)

    async def run(self):
        async with self._redis.pubsub() as pubsub:
            await pubsub.subscribe(self._channel)
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    commit_json = message['data'].decode('utf-8')
                    commit = DNSCommit.model_validate_json(commit_json)
                    self.__apply_commit(commit)

class DNSTaskProducer:
    def __init__(
        self,
        redis: redis.Redis,
        channel: str
    ) -> None:
        self._redis = redis
        self._channel = channel

    async def enqueue_commit(self, commit: DNSCommit):
        commit_json = commit.model_dump_json()
        await self._redis.publish(self._channel, commit_json)