# -*- coding: utf-8 -*-
from collections import Counter

from common.logger import logger
from common.models import Species


class GameMonitor:
    """Class to record game details"""

    def __init__(self):
        self._server_config = None

        self._game_parameters = None
        self._game_counter = None
        self._players = None
        self._game_details = None
        self._all_games = []
        self.reset()

    @staticmethod
    def _get_summary(ls):
        return Counter(ls).most_common(len(Species))

    @property
    def summary(self):
        return self._get_summary(self._game_counter)

    @property
    def players(self):
        return " vs. ".join([f"{ele['name']} ({ele['species'].name})" for ele in self._players])

    @property
    def starting_species(self):
        if not self._game_details:  # todo: details only updated after the end of a game
            return ""
        return self._game_details[-1]['starting_species']

    @property
    def global_summary(self):
        return [self._get_summary(ls) for ls in self._all_games]

    def __len__(self):
        return len(self._game_counter)

    def add_server_config(self, **kwargs):
        self._server_config = kwargs

    def add_game(self, **kwargs):
        self._game_parameters.update(kwargs)
        logger.info(f"Game parameters: {kwargs}")

    def add_player(self, name, species):
        self._players.append(dict(name=name, species=species))

    def append(self, winning_species: Species, starting_species: Species, nb_rounds: int):
        self._game_counter.append(winning_species)
        self._game_details.append({"starting_species": starting_species,
                                   "nb_rounds": nb_rounds,
                                   "winner": winning_species})

    def reset(self):
        self._game_parameters = {}
        self._game_counter = []
        self._players = []
        self._game_details = []
        self._all_games.append({"parameters": self._game_parameters, "players": self._players,
                                "results": self._game_counter, "details": self._game_details})

    def __str__(self):
        res = f"Game monitor (server: {self._server_config}):\n"
        # f"Game map: {self._game_parameters}\n"
        for i, game in enumerate(self._all_games):
            res += f"Game set #{i} summary: " \
                   f"Parameters: {game['parameters']}" \
                   f"Players: {game['players']}\n" \
                   f"Results: {self._get_summary(game['results'])}\n" \
                   f"Details: {game['details']}\n"""
        return res
