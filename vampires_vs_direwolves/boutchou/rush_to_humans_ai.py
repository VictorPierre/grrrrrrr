# -*- coding: utf-8 -*-
from time import sleep

from common.logger import logger
from boutchou.abstract_ai import AbstractSafeAI
from boutchou.rules import NextMoveRule
from common.exceptions import SpeciesExtinctionException


WAIT_TIME = 0.1  # in seconds


class RushToHumansAI(AbstractSafeAI):
    """Rush to human groups, then random group, no split, for tests"""

    def _generate_move(self):
        try:
            old_position, number = next(self._map.species_position_and_number_generator(self._species))
        except StopIteration:
            raise SpeciesExtinctionException(f"{self._species} already extinct!")

        rules = NextMoveRule(self._map)
        new_position = rules.move_to_human(old_position)
        if new_position is None:
            new_position = rules.move_to_opponent(old_position)
        if new_position is None:
            new_position = rules.random_move(old_position)

        sleep(WAIT_TIME)  # wait WAIT_TIME second(s)
        return [(*old_position, number, *new_position)]
