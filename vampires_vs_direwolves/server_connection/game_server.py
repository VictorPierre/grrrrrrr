"""
Game server
"""
import socket  # for socket
from threading import Thread
from time import sleep
from typing import List, Tuple

from common.logger import logger

from common.exceptions import TooMuchConnections, PlayerCheatedException, PlayerTimeoutError, IncorrectCommandException
from common.xml_map_parser import XMLMapParser
from game_management.game_map import ServerGameMap
from game_management.map_viewer import MapViewer
from game_management.rule_checks import check_movements
from server_connection.config_connection import CONFIG
from common.models import DataType, Species, PlayerCommand, Command
from server_connection.server_models import ServerCommunication, AbstractServer


class GameServer(AbstractServer):
    """Client class

    >>> server = GameServer()
    >>> server.run()
    True
    """

    def __init__(self, config: dict = None, nb_players: int = 2,
                 max_rounds: int = 200, max_nb_games: int = 1, show_map=True):
        # noinspection PyTypeChecker
        super().__init__()
        self._sock: socket.socket = None
        self._config = config or CONFIG
        self._is_active = True
        self._clients = []
        self._nb_players = nb_players
        self._game_worker = GameServerManager(server=self,
                                              nb_players=self._nb_players,
                                              max_rounds=max_rounds,
                                              max_nb_games=max_nb_games,
                                              show_map=show_map)

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
        if not is_connected:  # todo: handle error
            return False
        self._sock.listen(self._nb_players)
        logger.info("Game Server waiting for a connection")

        while self._is_active and self._game_worker.is_active:
            try:
                connection, _client = self._sock.accept()
                self._clients.append(connection)
                self._game_worker.add(connection)
            except (OSError, IOError) as err:
                logger.error(f"Server error: {err}")
                logger.exception(err)
        self._clients = []
        logger.info("Game server closing...")
        return True


try:
    N, M, UPDATES = XMLMapParser().read_xml_map()
except Exception as _err:
    logger.debug("Failed to load XML map")
    logger.exception(_err)
    N, M, UPDATES = 5, 5, [(0, 2, 0, 10, 0), (3, 2, 0, 0, 10)]


class GameServerManager:
    def __init__(self, server: AbstractServer, nb_players: int, max_rounds: int, max_nb_games: int, show_map: bool):
        self._server = server
        self._is_active = True
        self._nb_players = nb_players
        self._connections = []
        self._game_thread = None
        self._game_map = ServerGameMap(show_map=show_map)
        self._players = {}
        self._max_rounds = max_rounds
        self._init_threads = []
        self._game_counter = []
        self._max_nb_games = max_nb_games

        self._updates: List[List[Tuple[int, int, int, int, int]]] = []
        self.init_game()

    @property
    def is_active(self):
        return self._is_active

    def init_game(self, n=N, m=M):
        self._game_map.load_map(n, m)
        self._updates = [UPDATES.copy()]
        self._game_map.update(self._updates[0])

    def init_players(self):
        for player in self._players:
            self._init(player)
        self._start()

    def reinit_game(self):
        self.init_game()
        self.init_players()

    def add(self, connection):
        if len(self._connections) >= self._nb_players:
            raise TooMuchConnections()
        if connection is None:
            raise ValueError("None")
        if len(self._players) == 0:
            self._players.update({connection: {"name": "", "species": Species.VAMPIRE}})
        else:
            self._players.update({connection: {"name": "", "species": Species.WEREWOLF}})
        if len(self._players) == self._nb_players:
            self.init_players()

    @staticmethod
    def fight(species_1, number_1, species_2, number_2):
        if species_2 is Species.NONE:
            return species_1, number_1
        if species_2 is Species.HUMAN:  # TODO
            return species_1, number_1
        return species_1, number_1  # TODO

    def update_game_map(self, movements: List[Tuple[int, int, int, int, int, int]], species: Species):
        ls_updates = []
        for old_x, old_y, nb_move, new_x, new_y in movements:
            update1 = (old_x, old_y, 0, 0, 0)
            # todo: battle computation
            target_species, target_nb = self._game_map.get_cell_species_and_number((new_x, new_y))
            res_species, res_nb = self.fight(species, nb_move, target_species, target_nb)
            update2 = res_species.to_cell((new_x, new_y), res_nb)
            ls_updates.append(update1)
            ls_updates.append(update2)
        self._game_map.update(ls_updates)
        self._updates.append(ls_updates)

    # #### COMMANDS TO RECEIVE ####
    # Receive commands from connexions

    def start_game(self, connexion):
        """Send NME command to server at the beginning"""
        n = ServerCommunication.receive_int(connexion)
        name = ServerCommunication.receive(connexion, nb_bytes=n, expected_type=DataType.STR)
        self._players[connexion]["name"] = name
        logger.info(f"SERVER: Received name '{name}' from connexion!")

    def move(self, connexion):
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
            check_movements(movements, self._game_map, self._players[connexion]["species"])
        except AssertionError as err:
            logger.error(f"{self._players[connexion]['name']} player cheated!")
            raise PlayerCheatedException(self._players[connexion]['name'])
        logger.debug(f"SERVER: Received MOV command!")

        self.update_game_map(movements, self._players[connexion]["species"])

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
        logger.info(f"SERVER: There are {nb_houses} human houses: {human_houses}")

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
        logger.info(f"SERVER: Sent updates to connection: {updates}")

    def map(self, connection):
        updates = self._updates[-1]
        ServerCommunication.send(connection, "MAP", len(updates), *updates)
        logger.info(f"SERVER: The map has been loaded!")

    def _init(self, connexion):
        def init_connection():
            if self._players.get(connexion, {}).get("name", None) is None:
                msg = ServerCommunication.receive_command(connexion)
                assert Command.from_string(msg) is PlayerCommand.NME
                self.start_game(connexion)
            else:
                ServerCommunication.empty_socket(connexion)
            self.set(connexion)
            self.hum(connexion)
            self.hme(connexion)
            self.map(connexion)

        thread = Thread(target=init_connection)
        self._init_threads.append(thread)
        thread.start()

    def _check_winner(self) -> Species:
        vampires_pos = self._game_map.find_species_position(Species.VAMPIRE)
        werewolves_pos = self._game_map.find_species_position(Species.WEREWOLF)
        if not len(vampires_pos):
            return Species.WEREWOLF
        if not len(werewolves_pos):
            return Species.VAMPIRE
        return Species.NONE

    def _play_one_round(self) -> Species:
        for player_connection, params in self._players.items():
            ServerCommunication.empty_socket(player_connection)
            self.upd(player_connection)

            try:
                msg = ServerCommunication.receive_command(player_connection)
                cmd = PlayerCommand.from_string(msg)
                assert cmd is PlayerCommand.MOV, f"Bad command {cmd}"
                self.move(player_connection)
            except (PlayerCheatedException, AssertionError) as err:
                logger.warning(err)
                return Species.get_opposite_species(params["species"])
            except PlayerTimeoutError as err:
                logger.warning(err)
                continue

            # Check if someone has won
            has_won = self._check_winner()
            if has_won is not Species.NONE:
                return has_won
        return Species.NONE

    def play(self):
        has_won = Species.NONE
        for _round in range(self._max_rounds):
            has_won = self._play_one_round()
            if has_won is not Species.NONE:
                break

        logger.info(f"Game #{len(self._game_counter)} ended. Winning species: {has_won}")
        self._game_counter.append(has_won)

        for player in self._players:
            self.end(player)

        if has_won is Species.NONE or len(self._game_counter) < self._max_nb_games:
            logger.info(f"Starting a new game (#{len(self._game_counter)})!")
            # sleep(0.1)
            self.reinit_game()
        else:
            logger.info(f"No more game to play! Summary of past games: {self._game_counter}")
            for player in self._players:
                self.bye(player)
            self._game_map.close()
            self._is_active = False

    def _start(self):
        if self._nb_players == 1:
            raise NotImplementedError("only 2 players implemented")
        for thread in self._init_threads:  # wait for initializing
            thread.join()
        self._game_thread = Thread(target=self.play)
        self._game_thread.start()
        logger.info("Game worker thread started!")


if __name__ == '__main__':
    while True:
        map_viewer = MapViewer()
        game_server = Thread(target=GameServer(max_nb_games=5).run)
        game_server.start()
        map_viewer.start()
        game_server.join()
        logger.debug("Game server closed")
        logger.info("End of program SERVER")
