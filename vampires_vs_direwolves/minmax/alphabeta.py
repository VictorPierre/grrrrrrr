"""
code an alphabeta algorithm
"""
import time
from copy import copy
from typing import Type

from common.logger import logger
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.game_map import compute_new_board
from minmax.abstract_heuristic import AbstractHeuristic
from minmax.abstract_possible_moves_computer import \
    AbstractPossibleMovesComputer


def propagate(alpha_betas, val):
    pass


class AlphaBetaSearch:

    def __init__(self, possible_moves_computer: Type[AbstractPossibleMovesComputer],
                 heuristic: Type[AbstractHeuristic], depth: int):
        self.move_computer = possible_moves_computer()
        self.heuristic = heuristic()
        self.depth = depth

    def compute(self, game_map: AbstractGameMap, specie: Species):
        logger.debug('START SEARCH!!!!!!!!!!!!!!!!!!!!!')
        # logger.debug('NEWWWWWW MAPPP', compute_new_board(
        #     game_map, (4, 5, 3, 4, 4))._map_table)
        best_move = None
        best_val = -1e6 - 1

        other_specie = Species.VAMPIRE if specie == Species.WEREWOLF else Species.WEREWOLF
        # logger.debug(f"{specie.name}, {other_specie.name}")
        states = [{
            'board': game_map,
            'moves': self.move_computer.compute(game_map, specie),
            'alpha': -1e6,
            'beta': 1e6
        }]
        logger.debug(f"MOVES STATE 0 {states[0]['moves']}")
        # time.sleep(2)

        while states:
            s = states[-1]
            depth = len(states)
            # logger.debug(f'ENTER WHILEE!!!!!!!!!!!!! {depth}')
            # if depth <= 3:
            #     logger.debug('ALPHABETA', s['alpha'], s['beta'], depth)
            # state is a leaf
            if depth >= self.depth or s['board'].game_over()[0]:
                val = self.heuristic.evaluate(s['board'], specie)
                logger.debug(" ".join(['LEAFFFFFFF', 'VAL', str(val),
                                       'OVER', str(s['alpha']), str(s['beta']),
                                       str(s['board'].game_over()[0])]))
                # logger.debug(s['board']._map_table)

                states.pop()
                if depth % 2 and states:  # maximize
                    states[-1]['beta'] = min(s['beta'], val)
                    states[-1]['alpha'] = max(s['alpha'], val)
                elif states:  # minimize
                    states[-1]['alpha'] = max(s['alpha'], val)

                if depth == 2:
                    logger.debug(
                        f"Update Best Moveeeeeeeeeee: {best_move} {s['mv']}")
                    logger.debug(f"best_val {str(s['beta'])}")
                    if s['beta'] > best_val:  # update best move
                        best_move = s['mv']
                        best_val = s['beta']
                    # time.sleep(5)

            elif s['alpha'] > s['beta']:  # prune the tree
                logger.debug('PRUNINNNNNNNG')
                states.pop()
                if depth == 2:
                    logger.debug(
                        f"Update Best Moveeeeeeeeeee: {best_move} {s['mv']}")
                    logger.debug(f"best_val {str(best_val)} {s['beta']}")
                    if s['beta'] > best_val:  # update best move
                        best_move = s['mv']
                        best_val = s['beta']
                    # time.sleep(5)

            elif not s['moves']:  # go back up in the tree
                # logger.debug('GO BACKKKK UPPPPP')
                states.pop()
                if states:
                    if depth % 2:  # minimize
                        states[-1]['beta'] = min(states[-1]
                                                 ['beta'], s['alpha'])
                    else:

                        states[-1]['alpha'] = max(states[-1]
                                                  ['alpha'], s['beta'])
                    logger.debug(
                        f"UPPPPPP {depth - 1} {states[-1]['alpha']} {states[-1]['beta']}")
                if depth == 2:
                    logger.debug(
                        f"Update Best Moveeeeeeeeeee: {best_move} {str(s['mv'])}")
                    logger.debug(f"best_val {str(best_val)} {str(s['beta'])}")
                    if s['beta'] > best_val:  # update best move
                        best_move = s['mv']
                        best_val = s['beta']
                    # time.sleep(5)

            else:  # continue exploring the tree
                move = s['moves'].pop(0)
                logger.debug(f'EXPLOREEEEEEEE {move}')
                new_board = compute_new_board(s['board'], move)
                new_moves = []
                if depth + 1 < self.depth:
                    if depth % 2:  # it will be our turn
                        logger.debug('other playyys')
                        new_moves = self.move_computer.compute(
                            new_board, other_specie)
                    else:
                        logger.debug('We plaayy')
                        new_moves = self.move_computer.compute(
                            new_board, specie)

                new_state = {
                    'board': new_board,
                    'moves': new_moves,
                    'alpha': s['alpha'],
                    'beta': s['beta']
                }
                if depth == 1:
                    logger.debug(f'Tesssssssssst Move {str(move)}')
                    new_state['mv'] = move,  # remeber the move
                states.append(new_state)
        logger.info(
            f'AlphaBeta result: move: {str(best_move)}  value: {str(best_val)}')
        return best_move, best_val
