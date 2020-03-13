# -*- coding: utf-8 -*-
import time
from collections import defaultdict
from threading import Thread
from typing import List, Optional, Tuple, Type

from boutchou import *  # import all AIs
from common.exceptions import GameProtocolException, PlayerTimeoutError
from common.logger import logger
from common.models import Command, DataType, Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.rule_checks import check_movements
from server_connection.client import Client
from game_management.game_map import GameMap
from common.models import Command, Species

DEBUG_MODE = True


class GameManager:
    """Main class to run

    # Start a game
    >>> GameManager().start()
    """

    def __init__(self, player_name: str = "Boutchou", server_config: dict = None,
                 ai_class: Type[AbstractAI] = DefaultAI, map_class: Type[AbstractGameMap] = GameMap):
        self._name: str = player_name
        self._client: Client = Client(config=server_config)
        self._ai: AbstractAI = ai_class()
        self._map: AbstractGameMap = map_class()
        logger.debug(f"AI: {self._ai.__class__.__name__}, Map type: {self._map.__class__.__name__}")
        self._species: Species = Species.NONE
        # noinspection PyTypeChecker
        self._initial_position: Tuple[int, int] = None

    # #### COMMANDS TO SEND ####
    # Send commands to server

    def start_game(self):
        """Send NME command to server at the beginning"""
        self._client.send("NME", len(self._name), self._name)
        logger.info(f"{self._name}: Sent our name '{self._name}' to server!")

    def move(self, movements: List[Tuple[int, int, int, int, int]]):
        """Send MOV command to server"""
        movements_export = []
        for movement in movements:
            movements_export.extend(movement)

        self._client.send("MOV", len(movements), *movements_export)
        logger.debug(f"{self._name}: Sent MOV command!")

    def _get_int(self) -> int:
        return self._client.receive_int()

    # #### COMMANDS TO RECEIVE ####
    # React to command sent by server

    def set(self):
        n = self._get_int()
        m = self._get_int()
        logger.info(f"{self._name}: Game map size: {n} x {m}")
        # Load the game
        self._map.load_map(n, m)
        self._ai.load_map(self._map)

    def hum(self):
        n = self._get_int()
        coord = []
        for i in range(n):
            x = self._get_int()
            y = self._get_int()
            coord.append((x, y))
        logger.info(f"{self._name}: There are {n} human houses: {coord}")

    def hme(self):
        x = self._get_int()
        y = self._get_int()
        logger.info(f"{self._name}: Starting point: ({x}, {y})")
        self._initial_position = (x, y)

    def end(self):
        logger.info(f"{self._name}: Game over!")

    def bye(self):
        logger.info(f"{self._name}: Bye!")

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
        self._map.update(changes)
        return n, changes

    def upd(self):
        n, changes = self._update()
        logger.info(f"{self._name}: There are {n} changes: {changes}")
        t0 = time.time()
        logger.info(f"{self._name}: It's our turn !")
        new_movements = self._ai.generate_move()
        if DEBUG_MODE:
            check_movements(new_movements, self._map, self._species)  # check moves correctness
        self.move(new_movements)  # MOV
        t1 = time.time()
        logger.info(
            f"{self._name}: Sent our moves to server in {t1 - t0}s: {new_movements}")

    def map(self):
        self._update()
        logger.info(f"{self._name}: The map has been loaded!")
        self._species = self._map.get_cell_species(self._initial_position)
        self._ai.load_species(self._species)
        logger.info(f"{self._name}: Our species is {self._species.name}!")

    # #### INTERACTIONS WITH SERVER ####

    def _execute_command(self, command: Command):
        func = getattr(self, command.value)
        return func()

    def _wait_server(self):
        logger.debug(f"{self._species}: Waiting for server answer...")
        message = self._client.receive()
        command = Command.from_string(message)
        logger.debug(f"{self._name}: Command received: '{command}'")
        if command is None:
            return None
        self._execute_command(command)
        return command

    # #### GAME PLAY ####

    def _play(self):
        command = None
        while command is not Command.END:
            command = self._wait_server()  # SET / HUM / HME / MAP / UPD / END

        command = self._wait_server()  # SET / BYE
        if command is Command.SET:
            return self._play()
        elif command is Command.BYE:
            self._client.stop()
            return None
        else:
            raise GameProtocolException(
                f"At the end of a game, server should send SET or BYE, got {command}")

    def start(self):
        is_connected = self._client.connect()
        if is_connected:
            try:
                self.start_game()  # NME
                self._play()
            except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError, TimeoutError,
                    PlayerTimeoutError) as err:
                logger.error(f"Connection error: {err}")
                logger.exception(err)
        logger.debug(f"{self._name}: GameManager closing...")


if __name__ == '__main__':
    while True:
        player1 = Thread(target=GameManager(player_name="Boutchou", ai_class=RushToHumansAI).start)
        player2 = Thread(target=GameManager(player_name="Boss", ai_class=MoveToBestHumans).start)
        player1.start()
        player2.start()
        player1.join()
        player2.join()
        logger.info("End of program")
        logger.info("Auto-restarting players servers...")
    