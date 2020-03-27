# -*- coding: utf-8 -*-
from time import sleep

from boutchou import AbstractSafeAI
from boutchou.rules import NextMoveRule
from game_management.map_helpers import get_first_species_position_and_number

WAIT_TIME = 1 * 0.11  # in seconds


class RulesSequence(AbstractSafeAI):
    """AI working with a list of rules.

    """
    def __init__(self):
        super().__init__()
        self._move_methods = []
        self._methods_args = []
        self._methods_kwargs = []

    def _generate_single_move(self, old_position, number):
        rules = NextMoveRule(self._map, self._species)
        new_position = None
        for i, move_method in enumerate(self._move_methods):
            args = self._methods_args[i] if len(self._methods_args) > i and self._methods_args[i] else tuple()
            kwargs = self._methods_kwargs[i] if len(self._methods_kwargs) > i and self._methods_kwargs[i] else {}
            new_position = getattr(rules, move_method)(old_position, *args, **kwargs)
            if new_position is not None:
                break

        return [(*old_position, number, *new_position)] if new_position else None

    def _generate_move(self):
        forbidden_moves_start = set()
        forbidden_moves_end = set()
        updates = []
        current_positions = self._map.find_species_position_and_number(self._species)
        for old_position, number in current_positions:

            if old_position in forbidden_moves_end:  # old position is already a destination: forbidden (rule #5)
                continue

            new_updates = self._generate_single_move(old_position, number)
            if not new_updates:
                continue
            new_updates = [upd for upd in new_updates if tuple(upd[3:]) not in forbidden_moves_start]  # rule #5
            if not new_updates:
                continue
            updates += new_updates
            forbidden_moves_start.add(old_position)
            forbidden_moves_end.update({upd[3:] for upd in new_updates})

        sleep(WAIT_TIME)  # wait WAIT_TIME second(s)
        return updates or None
