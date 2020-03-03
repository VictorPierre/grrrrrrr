# -*- coding: utf-8 -*-
import select
import socket
from abc import abstractmethod, ABC
from time import time, sleep
from typing import Union, Tuple

import numpy as np

from common.logger import logger
from common.models import DataType
from common.exceptions import PlayerTimeoutError
from server_connection.config_connection import CONFIG


class ServerCommunication:
    @staticmethod
    def empty_socket(connection):
        connection: socket.socket
        bytes_received = bytes()
        while 1:
            inputready, o, e = select.select([connection], [], [], 0.0)
            if len(inputready) == 0:
                break
            for s in inputready:
                bytes_received += s.recv(1)
        if bytes_received:
            logger.warning(f"Extra bytes received from server: {bytes_received}")
            return bytes_received

    @classmethod
    def create_package(cls, arg):
        if isinstance(arg, (int, np.integer)):
            return int(arg).to_bytes(1, "big", signed=False)
        elif isinstance(arg, (tuple, list)):
            package = bytes()
            for sub_arg in arg:
                sub_pack = cls.create_package(sub_arg)
                package += sub_pack
            return package
        elif isinstance(arg, str):
            return arg.encode(encoding="ascii")
        else:
            raise TypeError(arg)

    @classmethod
    def send(cls, connection, *args: Union[str, int, Tuple[int, ...]]):
        package = cls.create_package(args)
        logger.debug(f"Sent {args} !")
        connection.send(package)

    @staticmethod
    def decode(input_bytes: bytes, expected_type: DataType):
        if expected_type is DataType.STR:
            decoded_str = input_bytes.decode(encoding="ascii")
        elif expected_type == DataType.INT:
            decoded_str = int.from_bytes(input_bytes, "little")
        else:
            raise TypeError(f"Invalid type expected: {expected_type}")
        return decoded_str

    @classmethod
    def receive(cls, connection, nb_bytes: int = 3, expected_type: DataType = DataType.STR,
                timeout: float = 0) -> Union[int, str]:
        message = bytes()
        t0 = time()
        t1 = t0
        while len(message) < nb_bytes or (timeout and (t1 - t0) > timeout):
            message += connection.recv(nb_bytes - len(message))
            t1 = time()
        if timeout and (t1 - t0) > timeout:
            raise PlayerTimeoutError(connection)
        decoded_command = cls.decode(message, expected_type)
        return decoded_command

    @classmethod
    def receive_command(cls, connection, timeout: float = 0) -> str:
        cmd = cls.receive(connection, nb_bytes=3, expected_type=DataType.STR, timeout=timeout)
        logger.debug(f"Received command: {cmd}")
        return cmd

    @classmethod
    def receive_int(cls, connection, timeout: float = 0) -> int:
        msg_int = cls.receive(connection, nb_bytes=1, expected_type=DataType.INT, timeout=timeout)
        logger.debug(f"Received int: {msg_int}")
        return msg_int


class AbstractServer(ABC):
    def __init__(self, config: dict = None):
        # noinspection PyTypeChecker
        self._sock: socket.socket = None
        self._config = config or CONFIG
        self._is_active = True

    @property
    def host(self):
        return self._config.get("host", None)

    @property
    def port(self):
        return self._config.get("port", None)

    @property
    def auto_reload(self):
        return self._config.get("auto_reload", 0)

    @property
    def timeout(self):
        return self._config.get("timeout", 5)

    @abstractmethod
    def _connect(self):
        pass

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

    def stop(self):
        self._is_active = False
        if self._sock:
            self._sock.close()
            logger.debug("Server socket closed")


class AbstractWorker(ABC):
    @property
    @abstractmethod
    def is_active(self):
        return False

    @abstractmethod
    def add(self, connection: socket.socket):
        pass
