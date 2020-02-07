# -*- coding: utf-8 -*-
import time
from typing import List, Tuple, Optional

from boutchou.abstract_ai import AbstractAI
from boutchou.default_ai import DefaultAI
from common.logger import logger
from server_connection.client import Client
from game_management.game_map import GameMap
from common.models import Command, Type, Species


class GameManager:
    """Main class to run

    >>> GameManager().start()
    """
    def __init__(self, server_config: dict = None, ai: AbstractAI = None):
        self._client: Client = Client(config=server_config)
        self._is_connected = False
        self._ai = ai or DefaultAI()
        self._map: GameMap = None
        self._species: Species = None
        self._position: Tuple[int, int] = None

    # #### COMMANDS TO SEND ####
    # Send commands to server

    def start_game(self):
        self._client.send("NME", 3, "hey")
        logger.info("Sent NME command!")

    def move(self, movements: List[Tuple[int, int, int, int, int]]):
        assert len(movements) >= 1
        assert len(movements) <= 10000
        movements_export = []
        for movement in movements:
            movements_export.extend(movement)
        self._client.send("MOV", len(movements), *movements_export)
        logger.debug("Sent MOV command!")
    
    def _get_int(self) -> int:
        return self._client.receive(1, expected_type=Type.INT)

    # #### COMMANDS TO RECEIVE ####
    # React to command sent by server

    def set(self) -> Command:
        n = self._get_int()
        m = self._get_int()
        logger.info(f"Game map size: {n} x {m}")
        # Load the game
        self._map = GameMap(n, m)
        self._ai.load_map(self._map)
        # Start the game and return the last command received (should be BYE)
        return self._play()

    def hum(self):
        n = self._get_int()
        coord = []
        for i in range(n):
            x = self._get_int()
            y = self._get_int()
            coord.append((x, y))
        logger.info(f"There are {n} human houses: {coord}")

    def hme(self):
        x = self._get_int()
        y = self._get_int()
        logger.info(f"Starting point: ({x}, {y})")
        self._position = (x, y)

    def end(self):
        logger.info("Game over!")

    def bye(self):
        logger.info("Bye!")

    def _update(self):
        n = self._get_int()
        changes = []
        for i in range(n):
            x = self._get_int()
            y = self._get_int()
            humans = self._get_int()
            vampires = self._get_int()
            werewolves = self._get_int()
            changes.append((x, y, humans, vampires, werewolves))
        return n, changes

    def upd(self):
        n, changes = self._update()
        logger.info(f"There are {n} changes: {changes}")
        t0 = time.time()
        logger.info("It's our turn !")
        new_movements = self._ai.generate_move()
        self.move(new_movements)
        logger.info(f"Sent our moves to server: {new_movements}")

    def map(self):
        n, changes = self._update()
        self._map.update(changes)
        self._map.show_map()
        logger.info(f"The map has been loaded!")
        self._species = self._map.get_cell_species(self._position)
        self._ai.load_species(self._species)
        logger.info(f"Our species is {self._species.name}!")

    # #### INTERACTIONS WITH SERVER ####

    @staticmethod
    def _interpret_message(message: str) -> Command:
        try:
            command = Command[message]
        except KeyError as _err:
            logger(f"Error: server sent an invalid command: {message}")
            return None
        return command

    def _execute_command(self, command: Command):
        func = getattr(self, command.value)
        return func()

    def _wait_server(self):
        message = self._client.receive()
        command = self._interpret_message(message)
        logger.debug(f"Command received: '{command}'")
        if command is None:
            return None
        self._execute_command(command)
        return command

    # #### GAME PLAY ####

    def _play(self):
        command = None
        while command is not Command.END:
            command = self._wait_server()  # UPD / END

        return self._wait_server()  # SET / BYE

    def start(self):
        if self._client.connect():
            self.start_game()  # NME
            self._wait_server()  # SET
        logger.debug("GameManager closing...")


if __name__ == '__main__':
    GameManager().start()
    logger.info("End of program")
