import numpy as np

from alphabeta.abstract_possible_moves_computer import SimpleMoveComputer
from alphabeta.alphabeta import AlphaBetaSearch
from alphabeta.diag_move_computer import DiagMoveComputer
from alphabeta.num_dist_heur import NumberAndDistanceHeuristic
from alphabeta.objective_first_move_computer import ObjectiveFirstMoveComputer
from alphabeta.simple_heuristics import (ExpectationHeuristic,
                                         SpeciesRatioHeuristic)
from boutchou.abstract_ai import AbstractAI


class AlphaBetaAI(AbstractAI):

    def __init__(self):
        super().__init__()
        self.nodes = []
        self.alphas = []
        self.betas = []

        self.search = AlphaBetaSearch(
            possible_moves_computer=SimpleMoveComputer,
            heuristic=NumberAndDistanceHeuristic,
            depth=5,
        )

    def generate_move(self):
        move, blaaaaaaaa, nodes, alpha, beta = self.search.compute(
            self._map, self._species)

        self.nodes.append(nodes)
        self.alphas.append(alpha)
        self.betas.append(beta)
        print(
            f'STATS, round {len(self.nodes)}, nodes : {np.mean(self.nodes)}, alpha : {np.mean(self.alphas)}, betas {np.mean(self.betas)}')
        return move


class AlphaBetaSimple(AlphaBetaAI):
    def __init__(self):
        super().__init__()
        self.search = AlphaBetaSearch(possible_moves_computer=SimpleMoveComputer,
                                      heuristic=SpeciesRatioHeuristic,
                                      depth=3)


class AlphaBetaExpectation(AlphaBetaAI):
    def __init__(self):
        super().__init__()
        self.search = AlphaBetaSearch(possible_moves_computer=SimpleMoveComputer,
                                      heuristic=ExpectationHeuristic,
                                      depth=3)


class AlphaBetaDiag(AlphaBetaAI):
    def __init__(self):
        super().__init__()
        self.search = AlphaBetaSearch(
            possible_moves_computer=DiagMoveComputer,
            heuristic=NumberAndDistanceHeuristic,
            depth=7,
        )


class AlphaBetaObj(AlphaBetaAI):
    def __init__(self):
        super().__init__()
        self.search = AlphaBetaSearch(
            possible_moves_computer=ObjectiveFirstMoveComputer,
            heuristic=NumberAndDistanceHeuristic,
            depth=7,
        )
