from libknot.control import KnotCtl
from contextlib import asynccontextmanager
import redis.asyncio as redis

from .base_operations.config import get_config
from .base_transaction import BaseTransaction, TransactionState

from .task import DNSCommand, DNSTaskType, DNSCommit, DNSCommitType
from .message_broker import DNSTaskProducer

class KnotConfigTransaction(BaseTransaction):
    def __init__(
        self,
        ctl: KnotCtl,
        redis_path: str,
        channel_name: str
    ):
        super().__init__()
        self.ctl = ctl
        self._redis_path = redis_path
        self._channel_name = channel_name
        self._task_buffer: list[DNSCommand] = list()

    async def open(self):
        await super().open()
    
    async def commit(self):
        async with redis.from_url(self._redis_path) as r:
            producer = DNSTaskProducer(r, self._channel_name)
            await producer.enqueue_commit(
                DNSCommit(
                    type = DNSCommitType.conf,
                    zone_name = None,
                    tasks = self._task_buffer
                )
            )
        await super().commit()

    async def rollback(self):
        await super().rollback()

    async def get(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        flags: str | None = None,
        filters: str | None = None
    ):
        return get_config(
            self.ctl,
            section,
            identifier,
            item,
            flags,
            filters
        )
    
    async def set(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        data: str | None = None
    ):
        task = DNSCommand(
            type = DNSTaskType.conf_set,
            data = {
                "section": section,
                "identifier": identifier,
                "item": item,
                "data": data
            }
        )
        self._task_buffer.append(task)

    async def unset(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None
    ):
        task = DNSCommand(
            type = DNSTaskType.conf_set,
            data = {
                "section": section,
                "identifier": identifier,
                "item": item
            }
        )
        self._task_buffer.append(task)
    
@asynccontextmanager
async def get_knot_config_transaction(
    ctl: KnotCtl,
    redis_path: str,
    channel_name: str
):
    transaction = None
    try:
        transaction = KnotConfigTransaction(ctl, redis_path, channel_name)
        await transaction.open()
        yield transaction
    finally:
        if transaction is not None and await transaction.state == TransactionState.opened:
            await transaction.rollback()