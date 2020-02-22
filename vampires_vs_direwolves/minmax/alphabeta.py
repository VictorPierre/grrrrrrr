"""
code an alphabeta algorithm
"""
from copy import copy

from abstract_heuristic import AbstractHeuristic
from abstract_possible_moves_computer import AbstractPossibleMovesComputer
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_map import compute_new_board


def propagate(alpha_betas, val):


class AlphaBetaSearch():

    def __init__(self, possible_moves_computer: AbstractPossibleMovesComputer, heuristic: AbstractHeuristic, depth: int):
        self.move_computer = possible_moves_computer
        self.heuristic = heuristic
        self.depth = depth

    def compute_move(self, game_map: AbstractGameMap, specie: Species):

        best_move = None
        best_val = float('-inf')

        other_specie = Species.VAMPIRE if specie == Species.WEREWOLF else Species.WEREWOLF
        states = []
        states.append({
            'board': game_map,
            'moves': self.move_computer(game_map, specie),
            'alpha': float('-inf'),
            'beta': float('inf')
        })

        while states:
            s = states[-1]
            depth = len(states)
            # state is a leaf
            if depth >= self.depth or board_states[-1].GameOver:
                val = self.heuristic.evaluate(board_states[-1], specie)
                states.pop()
                if depth % 2:  # maximize
                    states[-1]['alpha'] = max(states[-1]['alpha'], val)
                else:  # minimize
                    states[-1]['beta'] = min(states[-1]['beta'], val)

            elif s[-1]['alpha'] > s[-1]['beta']:  # prune the tree
                states.pop()

            elif not s['moves']:  # go back up in the tree
                states.pop()
                if depth == 2:
                    if s['beta'] > best_val:  # update best move
                        best_move = s['mv']
                        best_val = s['beta']
                if depth % 2:  # minimize
                    states[-1]['alpha'] = max(states[-1]['alpha'], s['beta'])
                else:
                    states[-1]['beta'] = min(states[-1]['beta'], s['alpha'])

            else:  # continue exploring the tree
                move = s['moves'].pop(0)
                new_board = compute_new_board(s['board'], move)
                new_moves = []
                if depth + 1 < self.depth:
                    if depth % 2:  # it will be our turn
                        new_moves = self.move_computer(new_board, specie)
                    else:
                        new_moves = self.move_computer(new_board, other_specie)

                new_state = {
                    'board': new_board,
                    'moves': new_moves,
                    'alpha': s['alpha'],
                    'beta': s['beta']
                }
                if depth == 1:
                    new_state['mv'] = move  # remeber the move
                states.append(new_state)
        return best_move, best_val
