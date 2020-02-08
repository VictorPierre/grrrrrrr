# -*- coding: utf-8 -*-
from typing import Tuple, List, Union

import numpy as np

from common.logger import logger
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap


class NewGameMap(AbstractGameMap):
    """Game map storage is a numpy array: [[[species number (0 to 3), number of persons], ...], ...]

    Less optimized than GameMap for RandomAI
    """
    def __init__(self):
        super().__init__()

    def load_map(self, n: int, m: int):
        super().load_map(n, m)
        self._map_table = np.zeros((n, m, 2), int)

    def __get_cell(self, position: Tuple[int, int]) -> Tuple[int, int]:
        return self._map_table[position[1], position[0]]

    def __set_cell(self, position: Tuple[int, int], new_cell: Tuple[int, int]):
        self._map_table[position[1], position[0]] = new_cell

    def find_species_position(self, species: Species) -> List[Tuple[int, int]]:
        species_positions = []
        for y in range(self._n):
            for x in range(self._m):
                if self.__get_cell((x, y))[0] == species.value:
                    species_positions.append((x, y))
        logger.debug(f"Positions of {species.name}: {species_positions}")
        return species_positions

    def get_cell_species(self, position: Tuple[int, int]) -> Species:
        return Species(self.__get_cell(position)[0])

    def get_cell_species_and_number(self, position: Tuple[int, int]) -> Tuple[Species, int]:
        return Species(self.__get_cell(position)[0]), self.__get_cell(position)[1]

    def get_cell_species_count(self, position: Tuple[int, int], species: Union[Species, int]) -> int:
        ind_species = species if isinstance(species, int) else species.value
        if self.__get_cell(position)[0] == ind_species:
            return self.__get_cell(position)[1]
        return 0

    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        for update in ls_updates:
            non_zero_tab = np.nonzero(update[2:])[0]
            assert len(non_zero_tab) < 2
            ind = non_zero_tab[0] if non_zero_tab else 3
            species_value = update[int(ind + 2)] if ind < 3 else 0
            self.__set_cell(update[:2], (ind, species_value))
        logger.debug("Game map updated")

    def show_map(self):
        print(self._map_table)


class SimpleGameMap(AbstractGameMap):
    """Game map storage is a numpy array: [[[number of humans, number of vampires, number of werewolves], ...], ...]

    Less optimized than GameMap for RandomAI
    """
    def __init__(self):
        super().__init__()
        self._map_table = None

    def load_map(self, n: int, m: int):
        super().load_map(n, m)
        self._map_table = np.zeros((n, m, 3), int)

    @property
    def cells(self):
        """Cells generator"""
        for i in range(self._n):
            for j in range(self._m):
                yield self._map_table[i, j]

    def __get_cell(self, position: Tuple[int, int]) -> Tuple[int, int, int]:
        # position: (x, y) where (0, 0) is the upper-left corner
        return self._map_table[position[1], position[0]]

    def get_cell_species(self, position: Tuple[int, int]) -> Species:
        return Species.from_cell(self.__get_cell(position))

    def get_cell_species_and_number(self, position: Tuple[int, int]) -> Tuple[Species, int]:
        return Species.from_cell_to_species_and_number(self.__get_cell(position))

    def get_cell_species_count(self, position: Tuple[int, int], species: Union[Species, int]) -> int:
        return self.__get_cell(position)[species if isinstance(species, int) else species.value]

    def find_species_position(self, species: Species) -> List[Tuple[int, int]]:
        species_positions = []
        for x in range(self._m):
            for y in range(self._n):
                if self._map_table[y, x, species.value]:
                    species_positions.append((x, y))
        logger.debug(f"Positions of {species.name}: {species_positions}")
        return species_positions

    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        for update in ls_updates:
            x, y = update[1], update[0]
            self._map_table[x, y] = update[2:]
        logger.debug("Game map updated")

    def show_map(self):
        print(self._map_table)
