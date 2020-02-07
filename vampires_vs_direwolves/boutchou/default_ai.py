# -*- coding: utf-8 -*-
from random import randint

from boutchou.abstract_ai import AbstractAI
from common.logger import logger
from exceptions import SpeciesExtinctionException


class DefaultAI(AbstractAI):
    """Random IA for tests"""

    @staticmethod
    def _get_move_range(coord, max_coord):
        if coord == max_coord:
            range_coord = (-1, 0)
        elif coord == 0:
            range_coord = (0, 1)
        else:
            range_coord = (-1, 1)
        return range_coord

    def _random_move(self, initial_position):
        x, y = initial_position
        range_x = self._get_move_range(x, self._map.n)
        range_y = self._get_move_range(y, self._map.n)
        new_pos = (0, 0)
        while new_pos == (0, 0):
            new_pos = (randint(*range_x), randint(*range_y))
        return new_pos

    def generate_move(self):
        species_positions = self._map.find_species_position(self._species)
        if not species_positions:
            logger.warning("We lost !")
            raise SpeciesExtinctionException("We lost!")
        old_position = species_positions[0]
        number = self._map.get_cell(*old_position)[self._species.value]
        new_position = self._random_move(species_positions[0])
        return [(*old_position, number, *new_position)]
