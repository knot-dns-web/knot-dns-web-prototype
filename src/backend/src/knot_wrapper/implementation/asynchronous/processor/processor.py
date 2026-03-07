from typing import TypeVar

from queue import Queue, Empty
from concurrent.futures import Future

from .command import Command, CommandBatch, PriorityCommand
from .binder import CommandBinder

T = TypeVar("T")

class Processor:
    """
    Thread-safe процессор для обработки поступающих команд
    """

    def __init__(self, binder: CommandBinder) -> None:
        """
        Создание процессора
        
        :param binder: Маппер классов-команд на действия
        :type binder: CommandBinder
        """

        self.binder = binder

        # Два конвейера
        # Конвейер с приоритетными командами будет в приоритете над конвейером с пакетами команд
        self.priority_conveyor: Queue[tuple[PriorityCommand, Future]] = Queue()
        self.batch_conveyor: Queue[tuple[CommandBatch, Future]] = Queue()

    def add_priority_command(self, command: PriorityCommand):        
        """
        Добавление приоритетной команды на конвейер процессора

        Добавление может производиться из любого потока
        
        :param command: Команда для исполнения
        :type command: PriorityCommand
        :return: Future, в которую будет передан результат выполнения команды
        """
        future = Future()
        pair = (command, future)
        self.priority_conveyor.put(pair)
        return future
    
    def add_command_batch(self, command_batch: CommandBatch):
        """
        Добавление пакета команд на конвейер процессора

        Добавление может производиться из любого потока
        
        :param command_batch: Пакет команд
        :type command_batch: CommandBatch
        :return: Future, в которую будет передан результат выполнения команды
        """

        future = Future()
        pair = (command_batch, future)
        self.batch_conveyor.put(pair)
        return future

    def __call_command__(self, command: Command, handler):
        result = handler(command)
        return result
    
    def __get_handler__(self, command_type: type[Command]):
        if command_type not in self.binder:
            raise TypeError(f"Unknown priority command type {command_type}")
        handler = self.binder[command_type]
        return handler

    def __priority_conveyor_step__(self, command: PriorityCommand, future: Future):
        command_type = type(command)
        handler = self.__get_handler__(command_type)
        try:
            result = self.__call_command__(command, handler)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)

    def __buffer_conveyor__(self, conveyor: Queue[T]):
        buffer: list[T] = list()
        buffer_size = conveyor.qsize()
        if buffer_size < 0:
            return buffer
        for _ in range(buffer_size):
            pair = conveyor.get_nowait()
            buffer.append(pair)
        return buffer

    def __batch_conveyor_run__(self, first_item: tuple[CommandBatch, Future]):
        buffer = [first_item] + self.__buffer_conveyor__(self.batch_conveyor)

        for batch, future in buffer:
            for command in batch.commands:
                command_type = type(command)
                handler = self.__get_handler__(command_type)
                try:
                    result = self.__call_command__(command, handler)
                    if not future.done():
                        future.set_result(result)
                except Exception as e:
                    if not future.done():
                        future.set_exception(e)

    def run(self):
        """
        Запустить процессор для обработки команд на конвейере
        
        Запуск должен производиться из отдельного потока,
        так как данная операция блокирующая
        """

        while True:
            try:
                command, future = self.priority_conveyor.get(timeout=0.05)
                self.__priority_conveyor_step__(command, future)
                while not self.priority_conveyor.empty():
                    command, future = self.priority_conveyor.get()
                    self.__priority_conveyor_step__(command, future)
            except Empty:
                pass

            try:
                item = self.batch_conveyor.get(timeout=0.05)
                self.__batch_conveyor_run__(item)
            except Empty:
                pass

            