# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Tuple, Union

from common.models import Species


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

    @abstractmethod
    def show_map(self):
        """Show the game map. Format is not specified."""
        pass
