<<<<<<< HEAD
from alphabeta.abstract_heuristic import NumberAndDistanceHeuristic
from alphabeta.abstract_possible_moves_computer import SimpleMoveComputer
from alphabeta.alphabeta import AlphaBetaSearch
from boutchou.abstract_ai import AbstractAI
=======
from boutchou.abstract_ai import AbstractAI
from alphabeta.abstract_heuristic import NumberAndDistanceHeuristic
from alphabeta.abstract_possible_moves_computer import SimpleMoveComputer
from alphabeta.alphabeta import AlphaBetaSearch
>>>>>>> master


class AlphaBetaAI(AbstractAI):

    def __init__(self):
        self.search = AlphaBetaSearch(possible_moves_computer=SimpleMoveComputer,
                                      heuristic=NumberAndDistanceHeuristic,
<<<<<<< HEAD
                                      depth=5)
=======
                                      depth=3)
>>>>>>> master
        super().__init__()

    def generate_move(self):
        move, blaaaaaaaa = self.search.compute(self._map, self._species)
<<<<<<< HEAD
        #print('MOVE!!!!!!!!!!!!!', move, blaaaaaaaa, type(move))
=======
        print('MOVE!!!!!!!!!!!!!', move, blaaaaaaaa, type(move))
>>>>>>> master
        return [move[0]]
