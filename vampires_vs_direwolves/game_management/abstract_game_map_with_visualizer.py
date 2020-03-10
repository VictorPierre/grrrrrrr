# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Tuple

from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.map_viewer import MapViewer


class AbstractGameMapWithVisualizer(AbstractGameMap, ABC):
    def __init__(self):
        super().__init__()
        self._map_viewer: MapViewer = MapViewer()  # map visualizer

    @abstractmethod
    def load_map(self, n: int, m: int):
        super().load_map(n, m)
        self._map_viewer.load(self)

    @abstractmethod
    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        """Update map given a list of updates from server
        An update tuple has the following format: (position_x, position_y, nb humans, nb vampires, nb werewolves)
        """
        super().update(ls_updates)
        self._map_viewer.update(ls_updates)

    @property
    def winning_species(self) -> Species:
        winner = super().winning_species
        self._map_viewer.update_winner(winner)
        return winner

    def close(self):
        self._map_viewer.close()
