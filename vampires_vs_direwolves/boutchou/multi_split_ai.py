# -*- coding: utf-8 -*-
from time import sleep
from random import shuffle

from common.logger import logger
from boutchou.abstract_ai import AbstractSafeAI
from boutchou.rules import NextMoveRule
from common.models import Species

WAIT_TIME = 0.61  # in seconds


class MultiSplitAI(AbstractSafeAI):
    """Split a maximum to destabilize opposite AI computations"""

    def _generate_move(self):
        forbidden_moves_start = set()
        forbidden_moves_end = set()
        updates = []
        current_positions = self._map.find_species_position_and_number(self._species)
        shuffle(current_positions)
        for old_position, number in current_positions:
            if old_position in forbidden_moves_end:  # old position is already a destination: forbidden (rule #5)
                continue
            possible_moves = self._map.get_possible_moves(old_position, force_move=True,
                                                          forbidden_positions=forbidden_moves_start)
            shuffle(possible_moves)
            for i in range(len(possible_moves)):
                if i >= number:
                    break  # do not move more than possible
                if self._map.get_cell_species(possible_moves[i]) not in (Species.NONE, self._species):
                    continue  # do not move to humans or enemy
                if possible_moves[i] in forbidden_moves_start:
                    continue  # rule #5
                updates.append((*old_position, 1, *possible_moves[i]))
                forbidden_moves_start.add(old_position)
                forbidden_moves_end.add(possible_moves[i])
        logger.info(f"UPDATES MULTISPLIT : {updates}")
        sleep(WAIT_TIME)  # wait WAIT_TIME second(s)
        return updates or None
