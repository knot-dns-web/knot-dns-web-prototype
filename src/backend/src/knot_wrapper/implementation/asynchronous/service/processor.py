
from ..processor.command import Command
from ..processor.binder import create_command_binder, bind_command
from ..processor.processor import Processor

global_command_binder = create_command_binder()

def bind_command_global(command_type: type[Command]):
    global global_command_binder
    return bind_command(command_type, global_command_binder)

global_processor = Processor(global_command_binder)