
from ...service.processor import bind_command_global as bind_command
from ..core.zone import ZoneGet, ZoneSet, ZoneUnset, ZoneCommit, ZoneAbort, ZoneBegin

from ....base_operations.zone import get_zone, set_zone, unset_zone

@bind_command(ZoneGet)
def _get_zone(command: ZoneGet):
    return get_zone(
        command.ctl,
        command.zone,
        command.owner,
        command.type
    )

@bind_command(ZoneSet)
def _set_zone(command: ZoneSet):
    return set_zone(
        command.ctl,
        command.zone,
        command.owner,
        command.type,
        command.ttl,
        command.data
    )

@bind_command(ZoneUnset)
def _unset_zone(command: ZoneUnset):
    return unset_zone(
        command.ctl,
        command.zone,
        command.owner,
        command.type,
        command.data
    )

@bind_command(ZoneBegin)
def begin_config(command: ZoneBegin):
    ctl = command.ctl
    ctl.send_block(cmd="zone-begin", zone=command.zone_name) # type: ignore
    ctl.receive_block()

@bind_command(ZoneAbort)
def abort_config(command: ZoneAbort):
    ctl = command.ctl
    ctl.send_block(cmd="zone-abort")
    ctl.receive_block()

@bind_command(ZoneCommit)
def commit_config(command: ZoneCommit):
    ctl = command.ctl
    ctl.send_block(cmd="zone-commit")
    ctl.receive_block()