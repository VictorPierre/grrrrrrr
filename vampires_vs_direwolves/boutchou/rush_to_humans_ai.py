# -*- coding: utf-8 -*-
from random import randint
from time import sleep
from typing import Tuple

from boutchou.abstract_ai import AbstractAI
from common.logger import logger
from common.exceptions import SpeciesExtinctionException
from common.models import Species
from game_management.map_helpers import get_distances_to_a_species, get_next_move_to_destination

WAIT_TIME = 0.5  # in seconds


class RushToHumansAI(AbstractAI):
    """Rush to human groups, then random group, no split, for tests"""

    def _random_move(self, initial_position: Tuple[int, int]) -> Tuple[int, int]:
        possible_moves = self._map.get_possible_moves(initial_position, force_move=True)
        rand_ind = randint(0, len(possible_moves) - 1)
        new_pos = possible_moves[rand_ind]
        logger.debug(f"New position computed: {new_pos}")
        return new_pos

    def _get_move_to_human(self, pos):
        humans = get_distances_to_a_species(pos, self._map, species=Species.HUMAN)
        sorted_humans = sorted(humans, key=lambda x: humans[x][1], reverse=False)
        if not sorted_humans:
            return None
        new_pos = get_next_move_to_destination(pos, sorted_humans[0])  # WARN: not proof in case of split
        return new_pos

    def generate_move(self):
        species_positions = self._map.find_species_position(self._species)
        if not species_positions:
            logger.warning("We lost !")
            raise SpeciesExtinctionException("We lost!")
        old_position = species_positions[0]
        number = self._map.get_cell_species_count(old_position, self._species)

        new_position = self._get_move_to_human(old_position)
        if new_position is None:
            new_position = self._random_move(species_positions[0])
        sleep(WAIT_TIME)  # wait WAIT_TIME second(s)
        return [(*old_position, number, *new_position)]

