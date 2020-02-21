# -*- coding: utf-8 -*-
from typing import List, Tuple, Union

import numpy as np

from common.logger import logger
from common.models import Species, Singleton
from game_management.abstract_game_map import AbstractGameMap, AbstractGameMapWithVisualizer


class GameMap(AbstractGameMap):
    """Game map storage is a numpy array: [[[number of humans, number of vampires, number of werewolves], ...], ...]
    and three other numpy arrays of each character: [[number of persons, ...], ...]
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._human_map = None
        self._vampire_map = None
        self._werewolf_map = None

    def load_map(self, n: int, m: int):
        super().load_map(n, m)
        self._map_table = np.zeros((n, m, 3), int)
        self._human_map = np.zeros((n, m), int)
        self._vampire_map = np.zeros((n, m), int)
        self._werewolf_map = np.zeros((n, m), int)

    def get_species_map(self, species: Species):
        if species is Species.HUMAN:
            return self._human_map
        elif species is Species.VAMPIRE:
            return self._vampire_map
        elif species is Species.WEREWOLF:
            return self._werewolf_map
        else:
            logger.error(f"Invalid species '{species}'")
            return None

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
        non_zero_tab = np.nonzero(self.get_species_map(species))
        species_positions = []
        for i, j in zip(non_zero_tab[0], non_zero_tab[1]):
            species_positions.append((j, i))
        logger.debug(f"Positions of {species.name}: {species_positions}")
        return species_positions

    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        for update in ls_updates:
            x, y = update[1], update[0]
            self._map_table[x, y] = update[2:]
            self._human_map[x, y] = update[2]
            self._vampire_map[x, y] = update[3]
            self._werewolf_map[x, y] = update[4]
        logger.debug("Game map updated")
        super().update(ls_updates)

    def show_map(self):
        print(self._map_table)


class ServerGameMap(GameMap, AbstractGameMapWithVisualizer):
    def __init__(self, show_map=True):
        super().__init__(show_map=show_map)
