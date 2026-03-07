from dataclasses import dataclass

from ...processor.command import PriorityCommand

from libknot.control import KnotCtl

@dataclass(frozen=True)
class ConnectionOpen(PriorityCommand):
    path: str

@dataclass(frozen=True)
class ConnectionClose(PriorityCommand):
    ctl: KnotCtl