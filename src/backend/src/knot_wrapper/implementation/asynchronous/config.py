
from typing import Any
from libknot.control import KnotCtl
from ...transaction import KnotConfigTransaction, KnotConnection

from .processor.command import Command, CommandBatch
from .commands.core.config import ConfigGet, ConfigSet, ConfigUnset, ConfigCommit, ConfigBegin, ConfigAbort
from .processor.processor import Processor

from .versions.storage import VersionsStorage

global_knot_config_transaction_processor: Processor | None = None
def set_knot_config_transaction_processor(processor: Processor):
    global global_knot_config_transaction_processor
    global_knot_config_transaction_processor = processor

class KnotConfigTransactionMTImpl(KnotConfigTransaction):
    def __init__(self, connection: KnotConnection):
        super().__init__(connection)

        self.transaction_write_buffer: list[Command] = list()
        self.versions_storage = VersionsStorage()

    def open(self):
        self.transaction_write_buffer.clear()
    
    def commit(self):
        global global_knot_config_transaction_processor

        if global_knot_config_transaction_processor is None:
            return
        
        if len(self.transaction_write_buffer) == 0:
            return
        
        ctl = self.connection.get_ctl()
        if ctl is None:
            return

        command_batch = CommandBatch(
            (
                ConfigAbort(ctl),
                ConfigBegin(ctl),
            ) +
            tuple(self.transaction_write_buffer) +
            (
                ConfigCommit(ctl),
            )
        )
        self.transaction_write_buffer.clear()
        
        future = global_knot_config_transaction_processor.add_command_batch(command_batch)
        future.result()

    def rollback(self):
        self.transaction_write_buffer.clear()

    def get(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        flags: str | None = None,
        filters: str | None = None
    ) -> Any:
        global global_knot_config_transaction_processor

        if global_knot_config_transaction_processor is None:
            return

        ctl = self.connection.get_ctl()
        if ctl is None:
            return

        command = ConfigGet(
            ctl,
            section,
            identifier,
            item,
            flags,
            filters
        )
        future = global_knot_config_transaction_processor.add_priority_command(command)
        result = future.result()
        return result
    
    def set(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None,
        data: str | None = None
    ):
        global global_knot_config_transaction_processor

        ctl = self.connection.get_ctl()
        if ctl is None:
            return

        command = ConfigSet(
            ctl,
            section,
            identifier,
            item,
            data
        )
        self.transaction_write_buffer.append(command)

    def unset(
        self,
        section: str | None = None,
        identifier: str | None = None,
        item: str | None = None
    ):
        ctl = self.connection.get_ctl()
        if ctl is None:
            return
        
        command = ConfigUnset(
            ctl,
            section,
            identifier,
            item
        )
        self.transaction_write_buffer.append(command)