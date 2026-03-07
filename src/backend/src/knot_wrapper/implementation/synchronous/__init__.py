
from typing import Any
from libknot.control import KnotCtl
from ...transaction import KnotZoneTransaction, KnotConfigTransaction, KnotConnection

from ...transaction import set_knot_config_transaction_impl, set_knot_zone_transaction_impl, set_knot_ctl_transaction_impl

from ..base_operations.config import get_config, set_config, unset_config
from ..base_operations.zone import get_zone, set_zone, unset_zone

class KnotConnectionImpl(KnotConnection):
    def __init__(self) -> None:
        self.ctl: KnotCtl | None = None

    def open(self, path: str):
        self.ctl = KnotCtl()
        self.ctl.connect(path)
    
    def close(self):
        if self.ctl is not None:
            self.ctl.close()

    def get_ctl(self) -> KnotCtl | None:
        return self.ctl

class KnotZoneTransactionImpl(KnotZoneTransaction):
    def __init__(self, connection: KnotConnection):
        super().__init__(connection, None)

    def open(self):
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        ctl.send_block(cmd="zone-begin")
        ctl.receive_block()
    
    def commit(self):
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        ctl.send_block(cmd="zone-commit")
        ctl.receive_block()

    def rollback(self):
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        ctl.send_block(cmd="zone-abort")
        ctl.receive_block()
    
    def get(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None
    ):
        ctl = self.connection.get_ctl()
        if ctl is None:
            return

        return get_zone(
            ctl,
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
        ctl = self.connection.get_ctl()
        if ctl is None:
            return

        return set_zone(
            ctl,
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
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        return unset_zone(
            ctl,
            zone,
            owner,
            type,
            data
        )

class KnotConfigTransactionImpl(KnotConfigTransaction):
    def __init__(self, connection: KnotConnection):
        super().__init__(connection)

    def open(self):
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        ctl.send_block(cmd="conf-begin")
        ctl.receive_block()
    
    def commit(self):
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        ctl.send_block(cmd="conf-commit")
        ctl.receive_block()

    def rollback(self):
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        ctl.send_block(cmd="conf-abort")
        ctl.receive_block()

    def get(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        flags: str | None = None,
        filters: str | None = None
    ) -> Any:
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        return get_config(
            ctl,
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
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        return set_config(
            ctl,
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
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        return unset_config(
            ctl,
            section,
            identifier,
            item
        )

set_knot_config_transaction_impl(KnotConfigTransactionImpl)
set_knot_zone_transaction_impl(KnotZoneTransactionImpl)