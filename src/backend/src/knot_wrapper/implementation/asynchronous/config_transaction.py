from libknot.control import KnotCtl
from contextlib import asynccontextmanager
import redis.asyncio as redis

from ..base_operations.config import get_config, set_config, unset_config, begin_config, abort_config, commit_config
from .base_transaction import BaseTransaction, TransactionState

from .message_broker import DNSWorker, DNSTaskProducer

class KnotConfigTransaction(BaseTransaction):
    def __init__(
        self,
        ctl: KnotCtl,
        redis_path: str
    ):
        super().__init__()
        self.ctl = ctl
        self.redis_path = redis_path

    async def open(self):
        async with redis.from_url(self.redis_path) as r:
            producer = DNSTaskProducer(r, "DNSCommitAsync")
            await producer.enqueue_task("CHECK")
        await super().open()
    
    async def commit(self):
        async with redis.from_url(self.redis_path) as r:
            producer = DNSTaskProducer(r, "DNSCommitAsync")
            await producer.enqueue_task("CHECK")

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
        return set_config(
            self.ctl,
            section,
            identifier,
            item,
            data
        )

    async def unset(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None
    ):
        return unset_config(
            self.ctl,
            section,
            identifier,
            item
        )
    
@asynccontextmanager
async def get_knot_config_transaction(
    ctl: KnotCtl,
    redis_path: str
):
    transaction = None
    try:
        transaction = KnotConfigTransaction(ctl, redis_path)
        await transaction.open()
        yield transaction
    finally:
        if transaction is not None and await transaction.state == TransactionState.opened:
            await transaction.rollback()