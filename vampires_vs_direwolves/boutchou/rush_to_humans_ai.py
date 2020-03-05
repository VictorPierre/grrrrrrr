# -*- coding: utf-8 -*-

from boutchou.rules import RuleSequence


class RushToHumansAI(RuleSequence):
    """Rush to human groups, then rush to opponent, no split, for tests"""

    def __init__(self):
        super().__init__()
        self._move_methods = ["move_to_closest_human", "move_to_closest_opponent", "random_move"]


class MoveToBestHumans(RuleSequence):
    """Rush to best human groups, then rush to opponent, no split, for tests"""

    def __init__(self, coef_distance=0, coef_number=0):
        super().__init__()
        self._move_method = ["move_to_best_human", "move_to_closest_opponent", "random_move"]
        self._methods_kwargs = [dict(coef_distance=coef_distance, coef_number=coef_number)]
