# -*- coding: utf-8 -*-
from boutchou.rules import NextMoveRule
from boutchou.rules_sequence import RulesSequence


class RushToOpponentAI(RulesSequence):
    """Rush to human groups, then random group, no split, for tests"""

    def __init__(self):
        super().__init__()
        self._move_methods = ["move_to_closest_opponent"]


class MoveToHumanOrMoveToOpponentIfBetter(RulesSequence):
    """Rush to human groups, then random group, no split, for tests"""

    def __init__(self):
        super().__init__()
        self._move_methods = ["move_to_opponent_if_blocked", "move_to_closest_human", "move_to_closest_opponent"]
