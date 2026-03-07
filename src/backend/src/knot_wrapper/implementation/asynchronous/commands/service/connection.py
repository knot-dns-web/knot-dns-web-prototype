
from ...service.processor import bind_command_global as bind_command
from ..core.connection import ConnectionClose, ConnectionOpen

from libknot.control import KnotCtl

@bind_command(ConnectionOpen)
def open_connection(command: ConnectionOpen):
    connection = KnotCtl()
    connection.connect(command.path)
    return connection

@bind_command(ConnectionClose)
def close_connection(command: ConnectionClose):
    command.ctl.close()