# -*- coding: utf-8 -*-
from typing import Generator, List, Tuple, Union

import numpy as np

from battle_computer.battle_computer import BattleComputer
from common.logger import logger
from common.models import Singleton, Species
from game_management.abstract_game_map import AbstractGameMap


class GameMap(AbstractGameMap):
    """Game map storage is a numpy array: [[[number of humans, number of vampires, number of werewolves], ...], ...]
    and three other numpy arrays of each character: [[number of persons, ...], ...]
    """

    def __init__(self):
        super().__init__()
        self._human_map = None
        self._vampire_map = None
        self._werewolf_map = None

    def load_map(self, n: int, m: int):
        self._map_table = np.zeros((n, m, 3), int)
        self._human_map = np.zeros((n, m), int)
        self._vampire_map = np.zeros((n, m), int)
        self._werewolf_map = np.zeros((n, m), int)
        super().load_map(n, m)

    def load_board(self, n: int, m: int, map_table, human_map, vampire_map, werewolf_map):
        self._map_table = np.copy(map_table)
        self._human_map = np.copy(human_map)
        self._vampire_map = np.copy(vampire_map)
        self._werewolf_map = np.copy(werewolf_map)
        super().load_map(n, m)

    @property
    def vampire_map(self):
        return self._vampire_map

    @property
    def werewolf_map(self):
        return self._werewolf_map

    @property
    def human_map(self):
        return self._human_map

    def save_board(self):
        return self.n, self.m, self._map_table, self._human_map, self._vampire_map, self._werewolf_map

    def _get_species_map(self, species: Species):
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

    def species_position_generator(self, species: Species) -> Generator:
        non_zero_tab = np.nonzero(self._get_species_map(species))
        for i, j in zip(non_zero_tab[0], non_zero_tab[1]):
            yield j, i

    def count_species(self, species) -> int:
        return self._get_species_map(species).sum()

    def species_position_and_number_generator(self, species: Species) -> Generator:
        non_zero_tab = np.nonzero(self._get_species_map(species))
        table = self._get_species_map(species)
        for i, j in zip(non_zero_tab[0], non_zero_tab[1]):
            yield (j, i), table[i, j]

    @property
    def is_game_over(self) -> bool:
        # faster implementation than AbstractGameMap
        return bool(len(np.nonzero(self._get_species_map(Species.WEREWOLF))[0])
                    * len(np.nonzero(self._get_species_map(Species.VAMPIRE))[0]))

    def game_over(self) -> Tuple[bool, Species]:
        # also returns the winning specie
        if not np.sum(self._vampire_map):
            return True, Species.WEREWOLF
        elif not np.sum(self._werewolf_map):
            return True, Species.VAMPIRE
        else:
            return False, None

    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        for update in ls_updates:
            x, y = update[1], update[0]
            self._map_table[x, y] = update[2:]
            self._human_map[x, y] = update[2]
            self._vampire_map[x, y] = update[3]
            self._werewolf_map[x, y] = update[4]
        logger.debug("Game map updated")
        super().update(ls_updates)


def compute_new_board(map: GameMap, move: Tuple[int, int, int, int, int]) -> AbstractGameMap:
    new_map = GameMap()
    #print('MAAAAAAAAP', map._map_table, move)
    new_map.load_board(*map.save_board())

    y0, x0, num, y1, x1 = move[0], move[1], move[2], move[3], move[4]
    # print(x0, y0, new_map.n, new_map.m)
    # print(new_map._map_table[x0, y0])

    spec0, n0 = new_map.get_cell_species_and_number(move[:2])
    assert num <= n0
    # remove the moving population from former case
    m0 = new_map._get_species_map(spec0)
    new_map._map_table[x0, y0, int(spec0)] -= num
    m0[x0, y0] -= num

    spec1, n1 = new_map.get_cell_species_and_number(move[3:])

    if spec0 != spec1 and n1 > 0:  # fight
        # remove fighting population from arrival case
        m1 = new_map._get_species_map(spec1)
        #print('M1111111111111111111111', m1, spec1)
        m1[x1, y1] = 0
        # print(spec0, n0, 'VERSSUUUUUUUUS', spec1, n1)
        new_map._map_table[x1, y1, int(spec1)] = 0
        spec, n = BattleComputer((spec0, num), (spec1, n1)
                                 ).compute_one_battle_result()
        # print('WINNNNNNNNNNER', spec, n)
        if n > 0:
            # there is survivors
            mfin = new_map._get_species_map(spec)
            mfin[x1, y1] = n
            new_map._map_table[x1, y1, int(spec)] = n

    else:
        m0[x1, y1] += num
        new_map._map_table[x1, y1, int(spec0)] += num
    return new_map
