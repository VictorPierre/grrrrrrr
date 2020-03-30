import time

from alphabeta.abstract_heuristic import NumberAndDistanceHeuristic
from alphabeta.abstract_possible_moves_computer import SimpleMoveComputer
from alphabeta.alphabeta import AlphaBetaSearch
from alphabeta.alphabeta2 import AlphaBetaSearch2
from boutchou.abstract_ai import AbstractAI


class AlphaBetaAI(AbstractAI):

    def __init__(self):
        super().__init__()

        self.search = AlphaBetaSearch2(
            possible_moves_computer=SimpleMoveComputer,
            heuristic=NumberAndDistanceHeuristic,
            depth=5,
        )

    def generate_move(self):
        move, blaaaaaaaa = self.search.compute(self._map, self._species)
        print('MOVE!!!!!!!!!!!!!', move, blaaaaaaaa, type(move))
        time.sleep(2)
        # return [move[0]]
        return move
