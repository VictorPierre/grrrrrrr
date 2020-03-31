from abc import ABC, abstractmethod

import numpy as np

from alphabeta.abstract_possible_moves_computer import \
    AbstractPossibleMovesComputer
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.map_helpers import *


class DiagMoveComputer(AbstractPossibleMovesComputer):

    def compute(self, board: AbstractGameMap, specie):
        res = []
        try:
            pos, num = get_first_species_position_and_number(board, specie)
        except SpeciesExtinctionException:
            return res

        # add all diagonal moves
        n, m = board.n, board.m

        diag_moves = np.array([(-1, -1), (1, -1), (1, 1), (-1, 1),
                               ])
        diag_moves += list(pos)
        in_bound_d = (diag_moves[:, 0] >= 0) \
            & (diag_moves[:, 0] < m) \
            & (diag_moves[:, 1] >= 0) \
            & (diag_moves[:, 1] < n)

        for i in range(len(diag_moves)):
            if in_bound_d[i]:
                res.append((*pos, num, *diag_moves[i]))

        # add a straight move only if :
        #  - one of neighbours cells is occupied by greater number of units than us
        #  - it contains units but less than us
        straight_moves = np.array([(0, -1), (1, 0), (0, 1), (-1, 0)])
        straight_moves += list(pos)
        straight_moves = straight_moves
        in_bound_s = (straight_moves[:, 0] >= 0) \
            & (straight_moves[:, 0] < m) \
            & (straight_moves[:, 1] >= 0) \
            & (straight_moves[:, 1] < n)

        adj_moves = np.concatenate((diag_moves, [diag_moves[0]]))
        for i in range(len(straight_moves)):
            n0, n1, n2 = 0, 0, 0
            if not in_bound_s[i]:
                continue  # cell is outside of the board
            if in_bound_d[i]:
                n0 = board.get_cell_number(adj_moves[i])

            if (i < 3 and in_bound_d[i+1]) or (i == 3 and in_bound_d[0]):
                n1 = board.get_cell_number(adj_moves[i+1])

            n2 = board.get_cell_number(straight_moves[i])
            if (n0 > num) or (n1 > num) or (n2 <= num):
                res.append((*pos, num, *straight_moves[i]))
        return res
