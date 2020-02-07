"""
Client server to connect to game server
"""
import socket  # for socket
import struct  # to encode numbers
import numpy as np

from common.logger import logger
from server_connection.config_connection import CONFIG
from common.models import Type


class Client:
    """Client class

    >>> client = Client()
    >>> client.connect()
    True
    """

    def __init__(self, config: dict = None):
        self._sock: socket.socket = None
        self._config = config or CONFIG

    @property
    def host(self):
        return self._config["host"]

    @property
    def port(self):
        return self._config["port"]

    def connect(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self.host, self.port))
        except socket.error as err:
            logger.error(f"Failed to connect to {self.host}:{self.port}")
            return False
        logger.info(f"Client successfully connected to {self.host}:{self.port}")
        return True

    def send(self, *args):
        package = bytes()
        for arg in args:
            if isinstance(arg, (int, float, np.integer)):
                if isinstance(arg, float):  # TODO
                    logger.warn(f"Performance loss: float instead of int: {arg}")
                package += struct.pack("d", float(arg))
            else:
                package += arg.encode(encoding="ascii")
        self._sock.send(package)

    @staticmethod
    def decode(input_bytes: bytes, expected_type: Type):
        if expected_type is Type.STR:
            decoded_str = input_bytes.decode(encoding="ascii")
        elif expected_type == Type.INT:
            decoded_str = int.from_bytes(input_bytes, "little")
        else:
            raise TypeError(f"Invalid type expected: {expected_type}")
        return decoded_str

    def receive(self, nb_bytes: int = 3, expected_type: Type = Type.STR):
        command = bytes()
        while len(command) < nb_bytes:
            command += self._sock.recv(nb_bytes - len(command))
        decoded_command = self.decode(command, expected_type)
        # logger.debug(f"Received command: {decoded_command}")
        return decoded_command
