# -*- coding: utf-8 -*-
from boutchou.rules import NextMoveRule, RuleSequence


class RushToOpponentAI(RuleSequence):
    """Rush to human groups, then random group, no split, for tests"""

    def __init__(self):
        super().__init__()
        self._move_methods = ["move_to_closest_opponent"]
