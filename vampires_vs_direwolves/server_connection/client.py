"""
Client server to connect to game server
"""
import socket  # for socket
import struct  # to encode numbers
import enum

from logger import logger
from server_connection.config_connection import CONFIG


class Type(enum.Enum):
    STR = 0,
    INT = 1,


class Client:
    """Client class

    >>> client = Client()
    >>> client.connect()
    True

    >>> client.start()
    >>> client.receive_command()
    'SET'
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
        except socket.error as err:
            logger.error(f"Failed to connect to {client.host}:{client.port}")
            return False
        self._sock.connect((self.host, self.port))
        logger.info(f"Client successfully connected to {client.host}:{client.port}")
        return True

    def send_command(self, *args):
        package = bytes()
        for arg in args:
            if isinstance(arg, int):
                package += struct.pack("d", float(arg))
            else:
                package += arg.encode(encoding="ascii")
        self._sock.send(package)

    def start(self):
        self.send_command("NME", 3, "hey")
        logger.info("Sent NME command!")

    def decode(self, input_bytes: bytes, expected_type: Type):
        if expected_type is Type.STR:
            decoded_str = input_bytes.decode(encoding="ascii")
        elif expected_type == Type.INT:
            decoded_str = int.from_bytes(input_bytes, "little")
        else:
            raise TypeError(f"Invalid type expected: {expected_type}")
        return decoded_str

    def receive_command(self, nb_bytes: int = 3, expected_type: Type = Type.STR):
        command = bytes()
        while len(command) < nb_bytes:
            command += self._sock.recv(nb_bytes - len(command))
        decoded_command = self.decode(command, expected_type)
        logger.debug(f"Received command: {decoded_command}")
        return decoded_command

    def handle_received_command(self, command: str):
        func = getattr(CommandHandler(), command.lower())
        func(self)

    def get(self):
        command = self.receive_command()
        self.handle_received_command(command)


class CommandHandler:
    def set(self, client: Client):
        n = client.receive_command(1, expected_type=Type.INT)
        m = client.receive_command(1, expected_type=Type.INT)
        logger.info(f"Map size: {n} x {m}")

    def hum(self, client: Client):
        n = client.receive_command(1, expected_type=Type.INT)
        coord = []
        for i in range(n):
            x = client.receive_command(1, expected_type=Type.INT)
            y = client.receive_command(1, expected_type=Type.INT)
            coord.append((x, y))
        logger.info(f"There are {n} human houses: {coord}")

    def hme(self, client: Client):
        x = client.receive_command(1, expected_type=Type.INT)
        y = client.receive_command(1, expected_type=Type.INT)
        logger.info(f"Starting point: ({x}, {y})")


if __name__ == '__main__':
    client = Client()
    is_connected = client.connect()
    client.start()

    client.get()
    client.get()
    client.get()

    print(f"the socket has successfully connected to host {client.host} on port {client.port}")
