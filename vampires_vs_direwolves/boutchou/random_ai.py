# -*- coding: utf-8 -*-
from boutchou.rules_sequence import RulesSequence


class RandomAI(RulesSequence):
    """Random AI with no split, for tests"""

    def __init__(self):
        super().__init__()
        self._move_methods = ["random_move"]
