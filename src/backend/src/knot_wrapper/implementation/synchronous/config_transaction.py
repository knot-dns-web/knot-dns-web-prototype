from libknot.control import KnotCtl
from contextlib import contextmanager

from ..base_operations.config import get_config, set_config, unset_config, begin_config, abort_config, commit_config
from .base_transaction import BaseTransaction, TransactionState

class KnotConfigTransaction(BaseTransaction):
    def __init__(
        self,
        ctl: KnotCtl
    ):
        super().__init__()
        self.ctl = ctl

    def open(self):
        begin_config(self.ctl)
        super().open()
    
    def commit(self):
        commit_config(self.ctl)
        super().commit()

    def rollback(self):
        abort_config(self.ctl)
        super().rollback()

    def get(
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
    
    def set(
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

    def unset(
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
    
@contextmanager
def get_knot_config_transaction(
    ctl: KnotCtl
):
    transaction = None
    try:
        transaction = KnotConfigTransaction(ctl)
        transaction.open()
        yield transaction
    finally:
        if transaction is not None and transaction.state == TransactionState.opened:
            transaction.rollback()