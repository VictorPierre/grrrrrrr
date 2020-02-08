# -*- coding: utf-8 -*-
from random import randint
from time import sleep
from typing import Tuple

from boutchou.abstract_ai import AbstractAI
from common.logger import logger
from common.exceptions import SpeciesExtinctionException


class RandomAI(AbstractAI):
    """Random AI with no split, for tests"""

    @staticmethod
    def _get_move_range(coord: int, max_coord: int) -> Tuple[int, int]:
        if coord + 1 == max_coord:
            range_coord = (-1, 0)
        elif coord == 0:
            range_coord = (0, 1)
        else:
            range_coord = (-1, 1)
        return range_coord

    def _random_move(self, initial_position: Tuple[int, int]) -> Tuple[int, int]:
        x, y = initial_position
        range_x = self._get_move_range(x, self._map.m)
        range_y = self._get_move_range(y, self._map.n)
        shift_pos = (0, 0)
        while shift_pos == (0, 0):
            shift_pos = (randint(*range_x), randint(*range_y))
        logger.debug(f"New position shift computed: {shift_pos}")
        return initial_position[0] + shift_pos[0], initial_position[1] + shift_pos[1]

    def generate_move(self):
        species_positions = self._map.find_species_position(self._species)
        if not species_positions:
            logger.warning("We lost !")
            raise SpeciesExtinctionException("We lost!")
        old_position = species_positions[0]
        number = self._map.get_cell_species_count(old_position, self._species)
        new_position = self._random_move(species_positions[0])
        sleep(1)  # wait 1 second
        return [(*old_position, number, *new_position)]
