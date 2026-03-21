from libknot.control import KnotCtl
from contextlib import asynccontextmanager

from ..base_operations.zone import get_zone, set_zone, unset_zone, begin_zone, abort_zone, commit_zone
from .base_transaction import BaseTransaction, TransactionState

class KnotZoneTransaction(BaseTransaction):
    def __init__(
        self,
        ctl: KnotCtl,
        redis_path: str,
        zone_name: str | None = None
    ):
        super().__init__()
        self.ctl = ctl
        self.redis_path = redis_path
        self.zone_name = zone_name

    async def open(self):
        await super().open()
    
    async def commit(self):
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
        return set_zone(
            self.ctl,
            zone,
            owner,
            type,
            ttl,
            data
        )

    async def unset(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None,
        data: str | None = None
    ):
        return unset_zone(
            self.ctl,
            zone,
            owner,
            type,
            data
        )
    
@asynccontextmanager
async def get_knot_zone_transaction(
    ctl: KnotCtl,
    redis_path: str,
    zone_name: str | None = None
):
    transaction = None
    try:
        transaction = KnotZoneTransaction(ctl, redis_path, zone_name)
        await transaction.open()
        yield transaction
    finally:
        if transaction is not None and await transaction.state == TransactionState.opened:
            await transaction.rollback()