from libknot.control import KnotCtl
from contextlib import contextmanager

from ..base_operations.zone import get_zone, set_zone, unset_zone, begin_zone, abort_zone, commit_zone, status_zone, backup_zone, restore_zone, flush_zone
from .base_transaction import BaseTransaction, TransactionState

from ...error.base_error import KnotError, KnotCtlError

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
        try:
            begin_zone(self.ctl, self.zone_name)
            super().open()
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)
    
    def commit(self):
        try:
            commit_zone(self.ctl, self.zone_name)
            flush_zone(self.ctl, self.zone_name)
            super().commit()
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)

    def rollback(self):
        try:
            abort_zone(self.ctl, self.zone_name)
            super().rollback()
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)
    
    def get(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None
    ):
        try:
            return get_zone(
                self.ctl,
                zone,
                owner,
                type
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)
    
    def set(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None,
        ttl: str | None = None,
        data: str | None = None
    ):
        try:
            return set_zone(
                self.ctl,
                zone,
                owner,
                type,
                ttl,
                data
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)

    def unset(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None,
        data: str | None = None
    ):
        try:
            return unset_zone(
                self.ctl,
                zone,
                owner,
                type,
                data
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)
    
    def status(
        self,
        zone: str | None = None,
        filters: str | None = None
    ):
        try:
            return status_zone(
                self.ctl,
                zone,
                filters
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)

    def backup(
        self,
        zone: str | None = None,
        dir_path: str | None = None,
        filters: str | None = None
    ):
        try:
            return backup_zone(
                self.ctl,
                zone,
                dir_path,
                filters
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)

    def restore(
        self,
        zone: str | None = None,
        dir_path: str | None = None
    ):
        try:
            return restore_zone(
                self.ctl,
                zone,
                dir_path
            )
        except KnotCtlError as e:
            raise KnotError.from_raw_error(e)
    
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