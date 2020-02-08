"""
Client server to connect to game server
"""
import socket  # for socket
from time import sleep
from typing import Union

import numpy as np

from common.logger import logger
from server_connection.config_connection import CONFIG
from common.models import DataType


class Client:
    """Client class

    >>> client = Client()
    >>> client.connect()
    True
    """

    def __init__(self, config: dict = None):
        # noinspection PyTypeChecker
        self._sock: socket.socket = None
        self._config = config or CONFIG

    @property
    def host(self):
        return self._config.get("host", None)

    @property
    def port(self):
        return self._config.get("port", None)

    @property
    def auto_reload(self):
        return self._config.get("auto_reload", 0)

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

    def connect(self):
        counter = 0
        is_connected = False
        while not is_connected and counter <= self.auto_reload:
            if counter:
                logger.info(f"Connection failed. Trying to reconnect in 2 seconds ({counter}/{self.auto_reload})...")
                sleep(2)
            is_connected = self._connect()
            counter += 1
        return is_connected

    def send(self, *args: Union[str, int]):
        package = bytes()
        for arg in args:
            if isinstance(arg, (int, float, np.integer)):
                if isinstance(arg, float):  # TODO
                    logger.warn(f"Performance loss: float instead of int: {arg}")
                package += int(arg).to_bytes(1, "big", signed=False)
            else:
                package += arg.encode(encoding="ascii")
        self._sock.send(package)

    @staticmethod
    def decode(input_bytes: bytes, expected_type: DataType):
        if expected_type is DataType.STR:
            decoded_str = input_bytes.decode(encoding="ascii")
        elif expected_type == DataType.INT:
            decoded_str = int.from_bytes(input_bytes, "little")
        else:
            raise TypeError(f"Invalid type expected: {expected_type}")
        return decoded_str

    def receive(self, nb_bytes: int = 3, expected_type: DataType = DataType.STR):
        message = bytes()
        while len(message) < nb_bytes:
            message += self._sock.recv(nb_bytes - len(message))
        decoded_command = self.decode(message, expected_type)
        # logger.debug(f"Received command: {decoded_command}")
        return decoded_command
