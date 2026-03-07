from collections.abc import Callable

from .command import Command

CommandHandler = Callable[[Command], None]
CommandBinder = dict[type[Command], CommandHandler]

def create_command_binder() -> CommandBinder:
    return dict()

def bind_command(command_type: type[Command], binder: CommandBinder):    
    def decorator(func):
        binder[command_type] = func
        return func
    return decorator