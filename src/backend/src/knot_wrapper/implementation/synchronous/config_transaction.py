from libknot.control import KnotCtl
from contextlib import contextmanager

from ..base_operations.config import get_config, set_config, unset_config, begin_config, abort_config, commit_config
from .base_transaction import BaseTransaction, TransactionState

from ...error.base_error import KnotError, KnotCtlError

class KnotConfigTransaction(BaseTransaction):
    def __init__(
        self,
        ctl: KnotCtl
    ):
        super().__init__()
        self.ctl = ctl

    def open(self):
        try:
            begin_config(self.ctl)
            super().open()
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)
    
    def commit(self):
        try:
            commit_config(self.ctl)
            super().commit()
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)

    def rollback(self):
        try:
            abort_config(self.ctl)
            super().rollback()
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)

    def get(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        flags: str | None = None,
        filters: str | None = None
    ):
        try:
            return get_config(
                self.ctl,
                section,
                identifier,
                item,
                flags,
                filters
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)
    
    def set(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        data: str | None = None
    ):
        try:
            return set_config(
                self.ctl,
                section,
                identifier,
                item,
                data
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)

    def unset(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None
    ):
        try:
            return unset_config(
                self.ctl,
                section,
                identifier,
                item
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)
    
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