from boutchou.abstract_ai import AbstractAI
from minmax.abstract_heuristic import NumberAndDistanceHeuristic
from minmax.abstract_possible_moves_computer import SimpleMoveComputer
from minmax.alphabeta import AlphaBetaSearch


class AlphaBetaAI(AbstractAI):

    def __init__(self):
        self.search = AlphaBetaSearch(possible_moves_computer=SimpleMoveComputer,
                                      heuristic=NumberAndDistanceHeuristic,
                                      depth=5)
        super().__init__()

    def generate_move(self):
        move, blaaaaaaaa = self.search.compute(self._map, self._species)
        print('MOVE!!!!!!!!!!!!!', move, blaaaaaaaa, type(move))
        return [move]
