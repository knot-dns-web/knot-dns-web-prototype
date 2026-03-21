from abc import ABC, abstractmethod

from ..transaction_state import TransactionState

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