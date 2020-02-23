# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from common.logger import logger
from common.models import Species
from game_management.map_viewer import MapViewer


class AbstractGameMap(ABC):
    """Abstract class defining the methods to describe a game map"""

    def __init__(self):
        self._n: int = 0  # number of lines
        self._m: int = 0  # number of columns
        self._map_table = None  # map storage

    @abstractmethod
    def load_map(self, n: int, m: int):
        """Create an empty map given its dimensions n (nb lines) and m (nb columns)"""
        assert n > 1 and m > 1
        self._n = n
        self._m = m

    n = property(lambda self: self._n)
    m = property(lambda self: self._m)
    map_table = property(lambda self: self._map_table)  # WARN: map_table format depends on the class !

    @abstractmethod
    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        """Update map given a list of updates from server
        An update tuple has the following format: (position_x, position_y, nb humans, nb vampires, nb werewolves)
        """
        pass

    @staticmethod
    def _get_move_range(coord: int, max_coord: int) -> Tuple[int, int]:
        """Get the range of possible moves for a coordinate x or y."""
        if coord + 1 == max_coord:
            range_coord = (-1, 1)
        elif coord == 0:
            range_coord = (0, 2)
        else:
            range_coord = (-1, 2)
        return range_coord

    def get_possible_moves(self, position: Tuple[int, int], force_move: bool = False) -> List[Tuple[int, int]]:
        """Return the list of possible moves from a position.

        If force_move, (x,y) is not returned in te list of possibilities.
        """
        x, y = position
        range_x = self._get_move_range(x, self.m)
        range_y = self._get_move_range(y, self.n)
        positions_set = set()
        for shift_x in range(*range_x):
            for shift_y in range(*range_y):
                positions_set.add((x + shift_x, y + shift_y))
        if force_move:
            positions_set.difference_update({position})
        assert 4 - int(force_move) <= len(positions_set) <= 9 - int(force_move)
        return list(positions_set)

    @property
    def positions(self):
        """Generator of positions

        >>> for x, y in self.positions:
        >>>     print(x, y)
        """
        for x in range(self._m):
            for y in range(self._n):
                yield x, y

    @abstractmethod
    def get_cell_species(self, position: Tuple[int, int]) -> Species:
        """Given a position, returns the species living in"""
        pass

    @abstractmethod
    def get_cell_species_and_number(self, position: Tuple[int, int]) -> Tuple[Species, int]:
        """Given a position, returns the tuple with the format: (species in the cell, number of persons)"""
        pass

    @abstractmethod
    def get_cell_species_count(self, position: Tuple[int, int], species: Union[Species, int]) -> int:
        """Given a position and a species (Species or int), returns the number of this species living in"""
        pass

    @abstractmethod
    def find_species_position(self, species: Species) -> List[Tuple[int, int]]:
        """Given a species, returns the list of positions where this species lives"""
        pass

    def close(self):
        pass


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

    def close(self):
        self._map_viewer.close()
