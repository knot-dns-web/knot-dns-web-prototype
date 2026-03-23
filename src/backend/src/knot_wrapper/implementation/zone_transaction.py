from libknot.control import KnotCtl
from contextlib import asynccontextmanager
import redis.asyncio as redis

from ..base_operations.zone import get_zone, status_zone
from .base_transaction import BaseTransaction, TransactionState

from .task import DNSCommand, DNSTaskType, DNSCommit, DNSCommitType
from .message_broker import DNSTaskProducer

class KnotZoneTransaction(BaseTransaction):
    def __init__(
        self,
        ctl: KnotCtl,
        redis_path: str,
        channel_name: str,
        zone_name: str | None = None
    ):
        super().__init__()
        self.ctl = ctl
        self._redis_path = redis_path
        self._zone_name = zone_name
        self._channel_name = channel_name
        self._task_buffer: list[DNSCommand] = list()

    async def open(self):
        await super().open()
    
    async def commit(self):
        async with redis.from_url(self._redis_path) as r:
            producer = DNSTaskProducer(r, self._channel_name)
            await producer.enqueue_commit(
                DNSCommit(
                    type = DNSCommitType.zone,
                    zone_name = self._zone_name,
                    tasks = self._task_buffer
                )
            )
        await super().commit()

    async def rollback(self):
        await super().rollback()
    
    async def get(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None
    ):
        return get_zone(
            self.ctl,
            zone,
            owner,
            type
        )
    
    async def set(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None,
        ttl: str | None = None,
        data: str | None = None
    ):
        task = DNSCommand(
            type = DNSTaskType.zone_set,
            data = {
                "zone": zone,
                "owner": owner,
                "type": type,
                "ttl": ttl,
                "data": data
            }
        )
        self._task_buffer.append(task)

    async def unset(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None,
        data: str | None = None
    ):
        task = DNSCommand(
            type = DNSTaskType.zone_unset,
            data = {
                "zone": zone,
                "owner": owner,
                "type": type,
                "data": data
            }
        )
        self._task_buffer.append(task)

    async def status(
        self,
        zone: str | None = None,
        filters: str | None = None
    ):
        return status_zone(
            self.ctl,
            zone,
            filters
        )

    async def backup(
        self,
        zone: str | None = None,
        dir_path: str | None = None,
        filters: str | None = None
    ):
        task = DNSCommand(
            type = DNSTaskType.zone_backup,
            data = {
                "zone": zone,
                "dir_path": dir_path,
                "filters": filters
            }
        )
        self._task_buffer.append(task)

    async def restore(
        self,
        zone: str | None = None,
        dir_path: str | None = None
    ):
        task = DNSCommand(
            type = DNSTaskType.zone_restore,
            data = {
                "zone": zone,
                "dir_path": dir_path
            }
        )
        self._task_buffer.append(task)
    
@asynccontextmanager
async def get_knot_zone_transaction(
    ctl: KnotCtl,
    redis_path: str,
    channel_name: str,
    zone_name: str | None = None
):
    transaction = None
    try:
        transaction = KnotZoneTransaction(ctl, redis_path, channel_name, zone_name)
        await transaction.open()
        yield transaction
    finally:
        if transaction is not None and await transaction.state == TransactionState.opened:
            await transaction.rollback()