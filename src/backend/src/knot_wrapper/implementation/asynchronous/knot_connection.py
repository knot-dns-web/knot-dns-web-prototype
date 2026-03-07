from libknot.control import KnotCtl
from ...transaction import KnotConnection

from .processor.processor import Processor

from .commands.core.connection import ConnectionOpen, ConnectionClose

global_knot_ctl_transaction_processor: Processor | None = None
def set_knot_ctl_transaction_processor(processor: Processor):
    global global_knot_ctl_transaction_processor
    global_knot_ctl_transaction_processor = processor

class KnotConnectionMTImpl(KnotConnection):
    def __init__(self) -> None:
        self.ctl: KnotCtl | None = None

    def open(self, path: str):
        global global_knot_ctl_transaction_processor

        if global_knot_ctl_transaction_processor is None:
            return
        
        future = global_knot_ctl_transaction_processor.add_priority_command(ConnectionOpen(path))
        result = future.result()
        self.ctl = result # type: ignore
    
    def close(self):
        global global_knot_ctl_transaction_processor

        if global_knot_ctl_transaction_processor is None:
            return
        
        if self.ctl is None:
            return
        
        future = global_knot_ctl_transaction_processor.add_priority_command(ConnectionClose(self.ctl))
        future.result()

    def get_ctl(self) -> KnotCtl | None:
        return self.ctl
    