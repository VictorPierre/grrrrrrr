# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import List, Tuple, Union, Generator, Set

from common.exceptions import GameMapOverPopulated
from common.logger import logger
from common.models import Species
from common.xml_map_parser import XMLMapParser


class AbstractGameMap(ABC):
    """Abstract class defining the methods to describe a game map"""

    def __init__(self):
        self._n: int = 0  # number of lines
        self._m: int = 0  # number of columns
        self._map_table = None  # map storage
        self._nb_updates = -1

    @staticmethod
    def get_map_param_from_file(path: str = ""):
        n, m, updates = XMLMapParser().read_xml_map(path)
        if sum(upd[2] + upd[3] + upd[4] for upd in updates) >= 256:
            raise GameMapOverPopulated(f"Too much population in map {path} (>255): {updates}")
        return n, m, updates

    def load_map_from_file(self, path: str = ""):
        n, m, updates = self.get_map_param_from_file(path)
        self.load_map(n, m)
        self.update([updates])

    @abstractmethod
    def load_map(self, n: int, m: int):
        """Create an empty map given its dimensions n (nb lines) and m (nb columns)"""
        assert n > 1 and m > 1
        self._n = n
        self._m = m
        self._nb_updates = -1

    n = property(lambda self: self._n)
    m = property(lambda self: self._m)
    update_number = property(lambda self: self._nb_updates)
    map_table = property(lambda self: self._map_table)  # WARN: map_table format depends on the class !

    @abstractmethod
    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        """Update map given a list of updates from server
        An update tuple has the following format: (position_x, position_y, nb humans, nb vampires, nb werewolves)
        """
        self._nb_updates += 1

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

    def get_possible_moves(self, position: Tuple[int, int], force_move: bool = False,
                           forbidden_positions: Set[Tuple[int, int]] = None) -> List[Tuple[int, int]]:
        """Return the list of possible moves from a position.

        :param position: position tuple (x, y) from which to move
        :param force_move: if True, (x,y) is not returned in the list of possibilities.
        :param forbidden_positions: optional set of forbidden position
        """
        forbidden_positions = forbidden_positions or set()
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
        positions_set -= forbidden_positions
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
    def get_cell_species_and_number(self, position: Tuple[int, int]) -> Tuple[Species, int]:
        """Given a position, returns the tuple with the format: (species in the cell, number of persons)"""
        pass

    def get_cell_species(self, position: Tuple[int, int]) -> Species:
        """Given a position, returns the species living in"""
        return self.get_cell_species_and_number(position)[0]

    def get_cell_number(self, position: Tuple[int, int]) -> int:
        """Given a position, returns the tuple with the format: (species in the cell, number of persons)"""
        return self.get_cell_species_and_number(position)[1]

    @abstractmethod
    def get_cell_species_count(self, position: Tuple[int, int], species: Union[Species, int]) -> int:
        """Given a position and a species (Species or int), returns the number of this species living in"""
        pass

    @abstractmethod
    def species_position_generator(self, species: Species) -> Generator:
        pass

    def find_species_position(self, species: Species) -> List[Tuple[int, int]]:
        """Given a species, returns the list of positions where this species lives"""
        species_positions = list(self.species_position_generator(species))
        logger.debug(f"Positions of {species.name}: {species_positions}")
        return species_positions

    @abstractmethod
    def species_position_and_number_generator(self, species: Species) -> Generator:
        pass

    def find_species_position_and_number(self, species: Species) -> List[Tuple[Tuple[int, int], int]]:
        """Given a species, returns the list of positions and number where this species lives"""
        return list(self.species_position_and_number_generator(species))

    def count_species(self, species) -> int:
        # WARN: not optimized: to be overridden
        return sum(nb for _pos, nb in self.species_position_and_number_generator(species))

    @property
    def is_game_over(self) -> bool:
        return bool(len(self.find_species_position(Species.VAMPIRE))
                    * len(self.find_species_position(Species.WEREWOLF)))

    @property
    def winning_species(self) -> Species:
        vampires_pos = self.find_species_position(Species.VAMPIRE)
        werewolves_pos = self.find_species_position(Species.WEREWOLF)
        if not len(vampires_pos):
            winner = Species.WEREWOLF
        elif not len(werewolves_pos):
            winner = Species.VAMPIRE
        else:
            winner = Species.NONE
        return winner

    def close(self):
        pass
