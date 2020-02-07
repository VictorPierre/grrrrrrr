# -*- coding: utf-8 -*-
from typing import List, Tuple

import numpy as np

from common.logger import logger
from common.models import Species


class GameMap:
    def __init__(self, n: int, m: int):
        self._n = n
        self._m = m
        self._map_table = np.zeros((n, m, 3))
        self._human_map = np.zeros((n, m))
        self._vampire_map = np.zeros((n, m))
        self._werewolf_map = np.zeros((n, m))

    map = property(lambda self: self._map_table)
    n = property(lambda self: self._n)
    m = property(lambda self: self._m)

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

    def get_cell(self, x: int, y: int):
        return self._map_table[y, x]

    def get_cell_species(self, position: Tuple[int, int]) -> Species:
        return Species.from_cell(self.get_cell(*position))

    def find_species_position(self, species: Species) -> List[Tuple[int, int]]:
        non_zero_tab = np.nonzero(self.get_species_map(species))
        species_positions = []
        for i, j in zip(non_zero_tab[0], non_zero_tab[1]):
            species_positions.append((j, i))
        return species_positions

    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        for update in ls_updates:
            x, y = update[1], update[0]
            self._map_table[x, y] = update[2:]
            self._human_map[x, y] = update[2]
            self._vampire_map[x, y] = update[3]
            self._werewolf_map[x, y] = update[4]
        logger.debug("Game map updated")

    def show_map(self):
        print(self._map_table)
