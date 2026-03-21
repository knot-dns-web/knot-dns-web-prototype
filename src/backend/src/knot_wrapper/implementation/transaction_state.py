from enum import Enum

class TransactionState(Enum):
    initial = 0
    opened = 1
    committed = 2
    cancelled = 3
    failed = 4