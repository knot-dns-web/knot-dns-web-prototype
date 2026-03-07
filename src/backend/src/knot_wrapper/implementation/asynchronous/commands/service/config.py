
from ...service.processor import bind_command_global as bind_command
from ..core.config import ConfigGet, ConfigSet, ConfigUnset, ConfigCommit, ConfigAbort, ConfigBegin

from ....base_operations.config import get_config, set_config, unset_config

@bind_command(ConfigGet)
def _get_config(command: ConfigGet):
    return get_config(
        command.ctl,
        command.section,
        command.identifier,
        command.item,
        command.flags,
        command.filters
    )

@bind_command(ConfigSet)
def _set_config(command: ConfigSet):
    return set_config(
        command.ctl,
        command.section,
        command.identifier,
        command.item,
        command.data
    )

@bind_command(ConfigUnset)
def _unset_config(command: ConfigUnset):
    return unset_config(
        command.ctl,
        command.section,
        command.identifier,
        command.item
    )

@bind_command(ConfigBegin)
def begin_config(command: ConfigBegin):
    ctl = command.ctl
    ctl.send_block(cmd="conf-begin")
    ctl.receive_block()

@bind_command(ConfigAbort)
def abort_config(command: ConfigAbort):
    ctl = command.ctl
    ctl.send_block(cmd="conf-abort")
    ctl.receive_block()

@bind_command(ConfigCommit)
def commit_config(command: ConfigCommit):
    ctl = command.ctl
    ctl.send_block(cmd="conf-commit")
    ctl.receive_block()