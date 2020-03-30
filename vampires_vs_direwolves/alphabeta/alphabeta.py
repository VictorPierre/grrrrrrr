"""
Inspired from http:aipython.org
"""

from copy import copy
from typing import Type

from alphabeta.abstract_heuristic import AbstractHeuristic
from alphabeta.abstract_possible_moves_computer import \
    AbstractPossibleMovesComputer
from common.logger import logger
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.game_map import compute_new_board


class AlphaBetaSearch2:

    def __init__(self, possible_moves_computer: Type[AbstractPossibleMovesComputer],
                 heuristic: Type[AbstractHeuristic], depth: int):
        self.move_computer = possible_moves_computer()
        self.heuristic = heuristic()
        self.max_depth = depth
        self.specie = None
        self.other_specie = None

    def compute(self, game_map: AbstractGameMap, specie: Species):
        self.specie = specie
        self.other_specie = Species.VAMPIRE if specie == Species.WEREWOLF else Species.WEREWOLF
        start_node = {
            'board': game_map,
            'max': True,
            'mv': None
        }

        score, path = self.minmax_alpha_beta(start_node, -1e6 - 1, 1e6 + 1)
        #print('PATHHHHH', path)
        move = path[0]['mv']
        return [move], score

    def is_leaf(self, node, depth):
        over = node['board'].game_over()[0]
        return over or depth >= self.max_depth

    def minmax_alpha_beta(self, node, alpha, beta, depth=0):
        """
            node is a Node, alpha and beta are cutoffs, depth is the depth
            returns value, path
            where path is a sequence of nodes that results in the value
        """
        best = []
        if self.is_leaf(node, depth):
            val = self.heuristic.evaluate(node['board'], self.specie)
            return val, [node]
        elif node['max']:
            moves = self.move_computer.compute(
                node['board'], self.specie)
            for move in moves:
                # create new node
                child = {
                    'board': compute_new_board(node['board'], move),
                    'max': False,
                    'mv': move
                }
                score, path = self.minmax_alpha_beta(
                    child, alpha, beta, depth+1)
                if score >= beta:  # beta pruning
                    b = [child] + path
                    return score, b
                if score > alpha:
                    alpha = score
                    best = [child] + path
            return alpha, best

        else:
            moves = self.move_computer.compute(
                node['board'], self.other_specie)
            for move in moves:
                # create new node
                child = {
                    'board': compute_new_board(node['board'], move),
                    'max': True,
                    'mv': move
                }
                score, path = self.minmax_alpha_beta(
                    child, alpha, beta, depth+1)
                if score <= alpha:  # alpha pruning
                    b = [child] + path
                    return score, b
                if score < beta:
                    beta = score
                    best = [child] + path
            return beta, best
