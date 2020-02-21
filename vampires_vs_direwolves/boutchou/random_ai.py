# -*- coding: utf-8 -*-
from random import randint
from time import sleep
from typing import Tuple

from boutchou.abstract_ai import AbstractAI
from common.logger import logger
from common.exceptions import SpeciesExtinctionException

WAIT_TIME = 0.005  # in seconds


class RandomAI(AbstractAI):
    """Random AI with no split, for tests"""

    def _random_move(self, initial_position: Tuple[int, int]) -> Tuple[int, int]:
        possible_moves = self._map.get_possible_moves(initial_position, force_move=True)
        rand_ind = randint(0, len(possible_moves) - 1)
        new_pos = possible_moves[rand_ind]
        logger.debug(f"New position computed: {new_pos}")
        return new_pos

    def generate_move(self):
        species_positions = self._map.find_species_position(self._species)
        if not species_positions:
            logger.warning("We lost !")
            raise SpeciesExtinctionException("We lost!")
        old_position = species_positions[0]
        number = self._map.get_cell_species_count(old_position, self._species)
        new_position = self._random_move(species_positions[0])
        sleep(WAIT_TIME)  # wait WAIT_TIME second(s)
        return [(*old_position, number, *new_position)]
