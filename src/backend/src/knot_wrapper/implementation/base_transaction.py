from abc import ABC, abstractmethod

from .transaction_state import TransactionState

class BaseTransaction(ABC):
    def __init__(self) -> None:
        self._state = TransactionState.initial

    @property
    async def state(self):
        return self._state
    
    @abstractmethod
    async def open(self):
        self._state = TransactionState.opened

    @abstractmethod
    async def commit(self):
        self._state = TransactionState.committed

    @abstractmethod
    async def rollback(self):
        self._state = TransactionState.cancelled