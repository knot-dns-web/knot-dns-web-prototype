from dataclasses import dataclass

from ...processor.command import PriorityCommand, Command

from libknot.control import KnotCtl

@dataclass(frozen=True)
class ConfigGet(PriorityCommand):
    ctl: KnotCtl
    section: str | None = None
    identifier: str | None = None
    item: str | None = None
    flags: str | None = None
    filters: str | None = None

@dataclass(frozen=True)
class ConfigSet(Command):
    ctl: KnotCtl
    section: str | None = None
    identifier: str | None = None
    item: str | None = None
    data: str | None = None

@dataclass(frozen=True)
class ConfigUnset(Command):
    ctl: KnotCtl
    section: str | None = None
    identifier: str | None = None
    item: str | None = None

@dataclass(frozen=True)
class ConfigBegin(Command):
    ctl: KnotCtl

@dataclass(frozen=True)
class ConfigAbort(Command):
    ctl: KnotCtl

@dataclass(frozen=True)
class ConfigCommit(Command):
    ctl: KnotCtl