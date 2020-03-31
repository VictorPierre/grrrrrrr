# -*- coding: utf-8 -*-

from boutchou.rules_sequence import RulesSequence


class AlmostExpertAI(RulesSequence):
    """Rush to best human groups, then rush to opponent, no split, for tests"""

    def __init__(self, coef_distance=0, coef_number=0):
        super().__init__()
        self._move_methods = ["escape_direct_threat", "move_to_humans_with_split", "move_to_friends"]
        self._methods_kwargs = [dict(coef_distance=coef_distance, coef_number=coef_number, split_possible=True)]