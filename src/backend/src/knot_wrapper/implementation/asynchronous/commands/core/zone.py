from dataclasses import dataclass

from ...processor.command import Command, PriorityCommand

from libknot.control import KnotCtl

@dataclass(frozen=True)
class ZoneGet(PriorityCommand):
    ctl: KnotCtl
    zone: str | None = None
    owner: str | None = None
    type: str | None = None

@dataclass(frozen=True)
class ZoneSet(Command):
    ctl: KnotCtl
    zone: str | None = None
    owner: str | None = None
    type: str | None = None
    ttl: str | None = None
    data: str | None = None

@dataclass(frozen=True)
class ZoneUnset(Command):
    ctl: KnotCtl
    zone: str | None = None
    owner: str | None = None
    type: str | None = None
    data: str | None = None

@dataclass(frozen=True)
class ZoneBegin(Command):
    ctl: KnotCtl
    zone_name: str | None

@dataclass(frozen=True)
class ZoneAbort(Command):
    ctl: KnotCtl

@dataclass(frozen=True)
class ZoneCommit(Command):
    ctl: KnotCtl