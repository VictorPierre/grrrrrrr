from abc import ABC, abstractmethod

import numpy as np

from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.map_helpers import *


class AbstractPossibleMovesComputer(ABC):

    @abstractmethod
    def compute(self, board: AbstractGameMap, specie: Species):
        return None


class SimpleMoveComputer(AbstractPossibleMovesComputer):

    def compute(self, board: AbstractGameMap, specie):

        try:
            pos, num = get_first_species_position_and_number(board, specie)
        except SpeciesExtinctionException:
            return []
        n, m = board.n, board.m

        moves = np.array([(-1, -1), (-1, 0), (-1, 1), (0, -1),
                          (0, 1), (1, -1), (1, 0), (1, 1)])

        moves += list(pos)

        moves = moves[(moves[:, 0] >= 0) & (moves[:, 0] < m) &
                      (moves[:, 1] >= 0) & (moves[:, 1] < n)]

        res = []
        for new_pos in moves:
            res.append((*pos, num, *new_pos))
        #print('COMPUTEEEEEEEEE NEW MMMOVES!!!!!!!', n, m, res, pos)
        return res
