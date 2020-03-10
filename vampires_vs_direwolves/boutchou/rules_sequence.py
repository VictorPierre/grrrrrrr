# -*- coding: utf-8 -*-
from time import sleep

from boutchou import AbstractSafeAI
from boutchou.rules import NextMoveRule
from game_management.map_helpers import get_first_species_position_and_number

WAIT_TIME = 1 * 0.11  # in seconds


class RulesSequence(AbstractSafeAI):
    """AI working with a list of rules.

    WARN: No split possible for the moment !
    """
    def __init__(self):
        super().__init__()
        self._move_methods = []
        self._methods_args = []
        self._methods_kwargs = []

    def _generate_move(self):
        old_position, number = get_first_species_position_and_number(self._map, self._species)  # WARN: only 1 position

        rules = NextMoveRule(self._map, self._species)
        new_position = None
        for i, move_method in enumerate(self._move_methods):
            args = self._methods_args if len(self._methods_args) > i and self._methods_args[i] else tuple()
            kwargs = self._methods_kwargs if len(self._methods_kwargs) > i and self._methods_kwargs[i] else {}
            new_position = getattr(rules, move_method)(old_position, *args, **kwargs)
            if new_position is not None:
                break

        sleep(WAIT_TIME)  # wait WAIT_TIME second(s)
        return [(*old_position, number, *new_position)] if new_position else None