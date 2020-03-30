from typing import List, Type

from common.models import Species
from game_management.game_map import GameMap
from alphabeta.abstract_heuristic import AbstractHeuristic


class HeuristicGroup(AbstractHeuristic):

    def __init__(self, heuristics: List[Type[AbstractHeuristic]], weight=1000):
        """

        :param heuristics: ordered list of heuristic classes
        :param weight: relative weight of the order in the list:
        1 for each heuristic has the same weight,
        1000 for the heuristic has a weight proportional to 1000 times power its opposite order (len - order)
        """
        super().__init__()
        self._heuristics = heuristics
        self._weight = weight

    def evaluate(self, game_map: GameMap, specie: Species):
        """ Evaluate the current map and return a number to score if it's in favour of the specie
        """
        heuristic_result = 0
        for i, heuristic in enumerate(self._heuristics):
            coef = self._weight ** (len(self._heuristics) - i) or 1
            heuristic_result += coef * heuristic().evaluate(game_map, specie)
        return heuristic_result
