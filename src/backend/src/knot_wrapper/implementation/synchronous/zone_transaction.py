from libknot.control import KnotCtl
from contextlib import contextmanager

from ..base_operations.zone import get_zone, set_zone, unset_zone, begin_zone, abort_zone, commit_zone
from .base_transaction import BaseTransaction, TransactionState

class KnotZoneTransaction(BaseTransaction):
    def __init__(
        self,
        ctl: KnotCtl,
        zone_name: str | None = None
    ):
        super().__init__()
        self.ctl = ctl
        self.zone_name = zone_name

    def open(self):
        begin_zone(self.ctl, self.zone_name)
        super().open()
    
    def commit(self):
        commit_zone(self.ctl, self.zone_name)
        super().commit()

    def rollback(self):
        abort_zone(self.ctl, self.zone_name)
        super().rollback()
    
    def get(
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
    
    def set(
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

    def unset(
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
    
@contextmanager
def get_knot_zone_transaction(
    ctl: KnotCtl,
    zone_name: str | None = None
):
    transaction = None
    try:
        transaction = KnotZoneTransaction(ctl, zone_name)
        transaction.open()
        yield transaction
    finally:
        if transaction is not None and transaction.state == TransactionState.opened:
            transaction.rollback()