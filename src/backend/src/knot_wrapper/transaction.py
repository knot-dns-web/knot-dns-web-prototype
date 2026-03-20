from typing import Any
from abc import ABC, abstractmethod
from contextlib import contextmanager
from libknot.control import KnotCtl

from enum import Enum

class KnotConnection(ABC):
    @abstractmethod
    def open(self, path: str):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def get_ctl(self) -> KnotCtl | None:
        pass

class TransactionState(Enum):
    initial = 0
    opened = 1
    committed = 2
    cancelled = 3
    failed = 4

class BaseTransaction(ABC):
    def __init__(self) -> None:
        self._state = TransactionState.initial

    @property
    def state(self):
        return self._state
    
    @abstractmethod
    def open(self):
        self._state = TransactionState.opened

    @abstractmethod
    def commit(self):
        self._state = TransactionState.committed

    @abstractmethod
    def rollback(self):
        self._state = TransactionState.cancelled

class KnotConfigTransaction(BaseTransaction):
    def __init__(
        self,
        connection: KnotConnection
    ):
        super().__init__()
        self.connection = connection

    @abstractmethod
    def get(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        flags: str | None = None,
        filters: str | None = None
    ) -> Any:
        pass
    
    @abstractmethod
    def set(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        data: str | None = None
    ):
        pass

    @abstractmethod
    def unset(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None
    ):
        pass

class KnotZoneTransaction(BaseTransaction):
    def __init__(
        self,
        connection: KnotConnection,
        zone_name: str | None
    ):
        super().__init__()
        self.connection = connection
        self.zone_name = zone_name

    @property
    def state(self):
        return self._state

    @abstractmethod
    def get(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None
    ) -> Any:
        pass

    @abstractmethod
    def set(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None,
        ttl: str | None = None,
        data: str | None = None
    ):
        pass

    @abstractmethod
    def unset(
        self,
        zone: str | None = None,
        owner: str | None = None,
        type: str | None = None,
        data: str | None = None
    ):
        pass

global_knot_path: str | None = None

global_knot_ctl_transaction_impl: type[KnotConnection] | None = None
global_knot_config_transaction_impl: type[KnotConfigTransaction] | None = None
global_knot_zone_transaction_impl: type[KnotZoneTransaction] | None = None

def set_knot_config_transaction_impl(impl: type[KnotConfigTransaction]):
    global global_knot_config_transaction_impl
    global_knot_config_transaction_impl = impl

def set_knot_zone_transaction_impl(impl: type[KnotZoneTransaction]):
    global global_knot_zone_transaction_impl
    global_knot_zone_transaction_impl = impl

def set_knot_ctl_transaction_impl(impl: type[KnotConnection]):
    global global_knot_ctl_transaction_impl
    global_knot_ctl_transaction_impl = impl

def set_knot_connection_path(path: str):
    global global_knot_path
    global_knot_path = path

@contextmanager
def get_knot_connection():
    global global_knot_ctl_transaction_impl, global_knot_path
    if global_knot_ctl_transaction_impl is None:
        return
    if global_knot_path is None:
        return
    
    connection = None
    try:
        connection = global_knot_ctl_transaction_impl()
        connection.open(global_knot_path)
        yield connection
    finally:
        if connection is not None:
            connection.close()

@contextmanager
def get_knot_config_transaction(
    connection: KnotConnection
):
    global global_knot_config_transaction_impl
    transaction = None
    try:
        if global_knot_config_transaction_impl is None:
            raise ValueError
        transaction = global_knot_config_transaction_impl(connection)
        transaction.open()
        yield transaction
    finally:
        if transaction is not None and transaction.state == TransactionState.opened:
            transaction.rollback()

@contextmanager
def get_knot_zone_transaction(
    connection: KnotConnection,
    zone_name: str | None = None
):
    global global_knot_zone_transaction_impl
    transaction = None
    try:
        if global_knot_zone_transaction_impl is None:
            raise ValueError
        transaction = global_knot_zone_transaction_impl(connection, zone_name)
        transaction.open()
        yield transaction
    finally:
        if transaction is not None and transaction.state == TransactionState.opened:
            transaction.rollback()

