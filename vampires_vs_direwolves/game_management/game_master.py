# -*- coding: utf-8 -*-
import socket
from threading import Thread
from time import sleep
from typing import Any, Dict, List, Tuple

from battle_computer.battle_computer import BattleComputer
from common.exceptions import (PlayerCheatedException, PlayerTimeoutError,
                               TooMuchConnections)
from common.logger import logger
from common.models import DataType, PlayerCommand, Species
from game_management.game_monitoring import GameMonitor
from game_management.map_viewer import MapViewer
from game_management.rule_checks import check_movements
from game_management.server_game_map import ServerGameMap
from server_connection.game_server import GameServer
from server_connection.server_models import AbstractWorker, ServerCommunication

WAIT_TIME = 1  # Between two games


class GameMasterWorker(AbstractWorker):
    """Game master including a server"""

    def __init__(self, nb_players: int, max_rounds: int, max_nb_games: int, auto_restart: int = 0, map_path: str = "",
                 use_expectation_instead_of_random=False):
        self._nb_players = nb_players
        self._max_rounds = max_rounds
        self._max_nb_games = max_nb_games
        self._auto_restart = auto_restart  # if negative, infinity loop
        self._use_expectation = use_expectation_instead_of_random

        self._map_path = map_path

        self._server: GameServer = None
        self._game_monitor = GameMonitor()
        self._game_map = ServerGameMap(self._game_monitor)
        self._starting_species = Species.VAMPIRE

        self._loop_thread = None
        self._game_thread = None

        self._players: Dict[socket.socket, Dict[str, Any]] = {}
        self._init_threads = []
        self._updates: List[List[Tuple[int, int, int, int, int]]] = []

        self._is_active = False

    # #### PROPERTIES ####

    @property
    def is_active(self):
        return self._is_active

    @property
    def nb_players(self):
        return self._nb_players

    @property
    def game_monitor(self):
        return self._game_monitor

    def get_player_name(self, connection):
        return f"{self._players[connection]['name']} ({self._players[connection]['species'].name})"

    def change_map_path(self, path: str):
        self._map_path = path

    # #### COMMANDS TO RECEIVE ####
    # Receive commands from connections

    def nme(self, connexion):
        """Send NME command to server at the beginning"""
        n = ServerCommunication.receive_int(connexion)
        name = ServerCommunication.receive(
            connexion, nb_bytes=n, expected_type=DataType.STR)
        self._players[connexion]["name"] = name
        self.game_monitor.add_player(
            name=name, species=self._players[connexion]['species'])
        logger.info(f"SERVER: Received name '{name}' from connexion!")

    @staticmethod
    def fight(species_1, number_1, species_2, number_2, use_expectation):
        return BattleComputer((species_1, number_1), (species_2, number_2)).compute_one_battle_result(
            use_expectation=use_expectation)

    def _update_game_map(self, movements: List[Tuple[int, int, int, int, int, int]], species: Species):
        ls_updates = []
        nb_old_pos = {}
        nb_new_pos = {}
        for old_x, old_y, nb_move, new_x, new_y in movements:
            previous_nb = nb_old_pos.get(
                (old_x, old_y), self._game_map.get_cell_species_and_number((old_x, old_y))[1])
            nb_old_pos[(old_x, old_y)] = previous_nb - nb_move
            nb_new_pos[(new_x, new_y)] = nb_new_pos.get(
                (new_x, new_y), 0) + nb_move

        for pos, nb in nb_old_pos.items():
            ls_updates.append(species.to_cell(pos, nb))

        for pos, nb in nb_new_pos.items():
            target_species, target_nb = self._game_map.get_cell_species_and_number(
                pos)
            res_species, res_nb = self.fight(
                species, nb, target_species, target_nb, self._use_expectation)
            update2 = res_species.to_cell(pos, res_nb)
            ls_updates.append(update2)

        self._game_map.update(ls_updates)
        self._updates.append(ls_updates)

    def mov(self, connexion):
        """Receive MOV command from client"""
        n = ServerCommunication.receive_int(connexion)
        movements = []
        for _i in range(n):
            _tmp = []
            for _j in range(5):
                _tmp.append(ServerCommunication.receive_int(connexion))
            movements.append(tuple(_tmp))

        # Check rules
        try:
            check_movements(movements, self._game_map,
                            self._players[connexion]["species"])
        except AssertionError as err:
            logger.error(
                f"{self._players[connexion]['name']} player cheated: {err}")
            raise PlayerCheatedException(self._players[connexion]['name'])
        logger.debug(f"SERVER: Received MOV command!")

        self._update_game_map(movements, self._players[connexion]["species"])

    # #### COMMANDS TO SEND ####
    # Send commands to clients

    def set(self, connection):
        n, m = self._game_map.n, self._game_map.m
        # Send game map dimensions
        ServerCommunication.send(connection, "SET", n, m)
        logger.info(f"SERVER: Game map size sent: {n} x {m}")

    def hum(self, connection):
        human_houses = self._game_map.find_species_position(Species.HUMAN)
        nb_houses = len(human_houses)
        ServerCommunication.send(connection, "HUM", nb_houses, *human_houses)
        logger.info(
            f"SERVER: There are {nb_houses} human houses: {human_houses}")

    def hme(self, connection):
        species = self._players[connection]["species"]
        x, y = self._game_map.find_species_position(species)[0]
        ServerCommunication.send(connection, "HME", x, y)
        logger.info(f"SERVER: Starting point: ({x}, {y})")

    def end(self, connection):
        ServerCommunication.send(connection, "END")
        logger.info(f"SERVER: Game over!")

    def bye(self, connection):
        ServerCommunication.send(connection, "BYE")
        logger.info(f"SERVER: Bye!")

    def upd(self, connection):
        updates = self._updates[-2:]  # get the last updates
        n = sum(len(_update) for _update in updates)
        ServerCommunication.send(connection, "UPD", n, *updates)
        logger.info(
            f"SERVER: Sent updates to {self.get_player_name(connection)}: {updates}")

    def map(self, connection):
        updates = self._updates[-1]
        ServerCommunication.send(connection, "MAP", len(updates), *updates)
        logger.info(f"SERVER: The map has been loaded!")

    # #### GAME LOGIC ####

    def _check_winner(self) -> Species:
        return self._game_map.winning_species

    def _play_one_species(self, player_connection):
        ServerCommunication.empty_socket(player_connection)
        self.upd(player_connection)

        try:
            msg = ServerCommunication.receive_command(
                player_connection, timeout=self._server.timeout)
            cmd = PlayerCommand.from_string(msg)
            assert cmd is PlayerCommand.MOV, f"Bad command {cmd}"
            self.mov(player_connection)
        except (PlayerCheatedException, AssertionError) as err:
            logger.warning(
                f"Player {self._players[player_connection]['name']} cheated: {err}")
            return Species.get_opposite_species(self._players[player_connection]["species"])
        except PlayerTimeoutError as err:
            logger.warning(err)
            return Species.NONE

        # Check if someone has won
        return self._check_winner()

    def _play_one_round(self, player_connection_1, player_connection_2) -> Species:
        # Player 1
        has_won = self._play_one_species(player_connection_1)

        # Check if someone has won
        if has_won is not Species.NONE:
            return has_won

        # Player 2
        has_won = self._play_one_species(player_connection_2)

        return has_won

    def _get_name_from_species(self, species):
        for conn, params in self._players.items():
            if params["species"] is species:
                return params["name"]
        return "Null"

    def play(self):
        # Find the first player
        player_connection_1, player_connection_2 = None, None
        assert len(
            self._players) == 2, f"Incorrect number of players: {len(self._players)}"
        for conn, params in self._players.items():
            if params["species"] is self._starting_species:
                player_connection_1 = conn
            else:
                player_connection_2 = conn
        assert isinstance(player_connection_1, socket.socket)
        assert isinstance(player_connection_2, socket.socket)

        has_won = Species.NONE
        nb_round = 0
        for _round in range(self._max_rounds):
            nb_round = _round
            has_won = self._play_one_round(
                player_connection_1, player_connection_2)
            if has_won is not Species.NONE:
                break

        if has_won == Species.NONE:
            winner_name = "none"
        elif self._players[player_connection_1]["species"] == has_won:
            winner_name = self._players[player_connection_1]["name"]
        else:
            winner_name = self._players[player_connection_2]["name"]

        logger.info(
            f"Game #{len(self._game_monitor)} ended. Winning species: {has_won.name} ({winner_name})")
        self._game_monitor.append(winning_species=self._get_name_from_species(has_won),
                                  starting_species=self._starting_species,
                                  nb_rounds=nb_round)

        for player in self._players:
            self.end(player)

        if has_won is Species.NONE or len(self._game_monitor) < self._max_nb_games:
            logger.info(f"Starting a new game (#{len(self._game_monitor)})!")
            sleep(WAIT_TIME)
            self.reinit_game()
        else:
            logger.info(
                f"No more game to play! Summary of past games: {self._game_monitor.summary}")
            for player in self._players:
                self.bye(player)
            self._game_map.close()
            self._is_active = False
            self._server.stop()
            self._players.clear()

    def _start_playing(self):
        if self._nb_players == 1:
            raise NotImplementedError("only 2 players implemented")
        for thread in self._init_threads:  # wait for initializing
            thread.join()
        self._game_thread = Thread(target=self.play)
        self._game_thread.start()
        logger.info("Game worker thread started!")

    def _init_server(self):
        self.game_monitor.add_server_config(name="default")
        self._server = GameServer(game_worker=self)

    def _init_map(self):
        n, m, updates = self._game_map.get_map_param_from_file(
            path=self._map_path)
        self._n = n
        self._m = m
        self._init_map_updates = updates
        self.game_monitor.add_game(file=self._map_path, n=n, m=m, map=updates)

    def _init_game(self):
        self._game_map.load_map(self._n, self._m)
        self._updates = [self._init_map_updates.copy()]
        self._game_map.update(self._updates[0])

    def _init(self, connexion):
        def init_connection():
            if self._players.get(connexion, {}).get("name", None) is None:
                msg = ServerCommunication.receive_command(connexion)
                assert PlayerCommand.from_string(msg) is PlayerCommand.NME
                self.nme(connexion)
            else:
                ServerCommunication.empty_socket(connexion)
            self.set(connexion)
            self.hum(connexion)
            self.hme(connexion)
            self.map(connexion)

        thread = Thread(target=init_connection)
        self._init_threads.append(thread)
        thread.start()

    def _init_players_and_start(self):
        for player in self._players:
            self._init(player)
        self._start_playing()

    def reinit_game(self):
        self._starting_species = Species.get_opposite_species(
            self._starting_species)
        self._init_game()
        self._init_players_and_start()

    def add(self, connection):
        if len(self._players) >= self._nb_players:
            raise TooMuchConnections(self._nb_players)
        if connection is None:
            raise ValueError("None")
        if len(self._players) == 0:
            self._players.update(
                {connection: {"name": None, "species": Species.VAMPIRE}})
        else:
            self._players.update(
                {connection: {"name": None, "species": Species.WEREWOLF}})
        if len(self._players) == self._nb_players:
            self._init_players_and_start()

    def loop(self):
        """Main loop"""
        counter = 0
        while not counter or counter != self._auto_restart + 1:
            if counter:
                logger.warning(
                    f"Auto-restarting server ({counter + 1}/{self._auto_restart + 1})...")
                self._game_monitor.reset()
            self._init_server()
            self._init_map()
            self._init_game()
            self._is_active = True
            self._server.start()
            self._server.join()
            self._is_active = False
            counter += 1

        logger.info("Game master closed")

    def start(self):
        self._loop_thread = Thread(target=self.loop)
        self._loop_thread.start()

    def stop(self):
        self._server.stop()
        self._loop_thread.join(timeout=1)

    def join(self):
        self._loop_thread.join()


if __name__ == '__main__':
    MapViewer().set_visible(True)
    game_master = GameMasterWorker(
        nb_players=2, max_rounds=100, max_nb_games=2, auto_restart=1)
    game_master.start()
    MapViewer().mainloop()
    game_master.join()
    print(game_master.game_monitor)
    logger.info("END OF GAME MASTER / SERVER")
