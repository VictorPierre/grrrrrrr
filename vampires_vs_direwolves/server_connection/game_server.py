"""
Game server
"""
import socket  # for socket
from threading import Thread

from common.exceptions import TooMuchConnections
from common.logger import logger

from server_connection.config_connection import CONFIG
from server_connection.server_models import AbstractServer


class GameServer(Thread, AbstractServer):
    """Client class

    >>> server = GameServer()
    >>> server.run()
    True
    """

    def __init__(self, config: dict = None, game_worker: 'GameMasterWorker' = None):
        super().__init__()
        # noinspection PyTypeChecker
        self._sock: socket.socket = None
        self._config = config or CONFIG.copy()
        self._game_worker = game_worker
        self._nb_connections = game_worker.nb_players
        self._is_active = True

    def _connect(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.bind((self.host, self.port))
        except (socket.error, OSError) as err:
            logger.error(f"Failed to connect to {self.host}:{self.port}")
            logger.exception(err)
            return False
        logger.info(f"Client successfully connected to {self.host}:{self.port}")
        return True

    def run(self):
        is_connected = self.connect()
        if not is_connected:
            return False
        self._sock.listen(self._nb_connections)
        logger.info("Game Server waiting for a connection")

        while self._is_active and self._game_worker.is_active:
            try:
                connection, _client = self._sock.accept()
                self._game_worker.add(connection)
            except (OSError, IOError) as err:
                logger.warning(f"Server error: {err}")
                # logger.exception(err)
            except TooMuchConnections as err:
                err_msg = f"Too much connections: {err}"
                if self._is_active and self._game_worker.is_active:
                    logger.error(err_msg)
                else:
                    logger.debug(err_msg)

        logger.info("Game server closed")
        return True
