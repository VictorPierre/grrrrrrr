from alphabeta.simple_heuristics import ExpectationHeuristic, SpeciesRatioHeuristic
from boutchou.abstract_ai import AbstractAI
from alphabeta.abstract_heuristic import NumberAndDistanceHeuristic
from alphabeta.abstract_possible_moves_computer import SimpleMoveComputer
from alphabeta.alphabeta import AlphaBetaSearch


class AlphaBetaAI(AbstractAI):

    def __init__(self):
        self.search = AlphaBetaSearch(possible_moves_computer=SimpleMoveComputer,
                                      heuristic=NumberAndDistanceHeuristic,
                                      depth=5)
        super().__init__()

    def generate_move(self):
        move, blaaaaaaaa = self.search.compute(self._map, self._species)
        #print('MOVE!!!!!!!!!!!!!', move, blaaaaaaaa, type(move))
        return [move[0]]


class AlphaBetaSimple(AlphaBetaAI):
    def __init__(self):
        self.search = AlphaBetaSearch(possible_moves_computer=SimpleMoveComputer,
                                      heuristic=SpeciesRatioHeuristic,
                                      depth=3)
        super().__init__()


class AlphaBetaExpectation(AlphaBetaAI):
    def __init__(self):
        self.search = AlphaBetaSearch(possible_moves_computer=SimpleMoveComputer,
                                      heuristic=ExpectationHeuristic,
                                      depth=3)
        super().__init__()
