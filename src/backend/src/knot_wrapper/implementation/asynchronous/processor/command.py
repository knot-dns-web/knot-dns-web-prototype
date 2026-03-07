from dataclasses import dataclass

class Command:
    pass

class PriorityCommand(Command):
    pass

@dataclass(frozen=True)
class CommandBatch(Command):
    commands: tuple[Command, ...]