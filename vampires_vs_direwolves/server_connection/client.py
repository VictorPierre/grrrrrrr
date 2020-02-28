"""
Client server to connect to game server
"""
import socket  # for socket
from typing import Union

from common.logger import logger

from common.models import DataType
from server_connection.server_models import AbstractServer, ServerCommunication


class Client(AbstractServer):
    """Client class

    >>> client = Client()
    >>> client.connect()
    True
    """

    def __init__(self, config: dict = None):
        super().__init__(config=config)

    def _connect(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self.host, self.port))
        except socket.error as err:
            logger.error(f"Failed to connect to {self.host}:{self.port}")
            logger.exception(err)
            return False
        logger.info(f"Client successfully connected to {self.host}:{self.port}")
        return True

    def send(self, *args: Union[str, int]):
        ServerCommunication.send(self._sock, *args)

    def receive(self, nb_bytes: int = 3, expected_type: DataType = DataType.STR):
        return ServerCommunication.receive(self._sock, nb_bytes=nb_bytes,
                                           expected_type=expected_type, timeout=self.timeout)

    def receive_int(self):
        return ServerCommunication.receive_int(self._sock, timeout=self.timeout)
