import functools
from random import randint
from typing import Tuple

from common.logger import logger
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.map_helpers import get_next_move_to_destination, get_distances_to_a_species


class NextMoveRule:
    """Class with rules"""

    def __init__(self, game_map: AbstractGameMap):
        self._game_map = game_map

    def no_move(self, position: Tuple[int, int], force_move=False) -> Tuple[int, int]:
        assert not force_move, "force_move attribute cannot be True for no_move method!"
        return position

    def safe_move(self, position, force_move=True, **_kwargs):
        possible_moves = self._game_map.get_possible_moves(position, force_move=force_move)
        assert len(possible_moves), f"No possible move from {position}! Map size may be too small."
        return possible_moves[0]

    def random_move(self, position: Tuple[int, int], force_move=True) -> Tuple[int, int]:
        possible_moves = self._game_map.get_possible_moves(position, force_move=force_move)
        rand_ind = randint(0, len(possible_moves) - 1)
        new_pos = possible_moves[rand_ind]
        return new_pos

    def move_to_human(self, pos):
        humans = get_distances_to_a_species(pos, self._game_map, species=Species.HUMAN)
        sorted_humans = sorted(humans, key=lambda x: humans[x][1], reverse=False)
        if not sorted_humans:
            return None
        new_pos = get_next_move_to_destination(pos, sorted_humans[0])  # WARN: not proof in case of split
        return new_pos

    def move_to_opponent(self, position):
        species = self._game_map.get_cell_species(position)
        assert species in (Species.VAMPIRE, Species.WEREWOLF), f"Bad species moving: {species}"
        opponents = get_distances_to_a_species(position, self._game_map, species=Species.get_opposite_species(species))
        sorted_opponents = sorted(opponents, key=lambda x: opponents[x][1], reverse=False)
        if not sorted_opponents:
            logger.error(f"No more opponent against {species}!")
            return None
        new_pos = get_next_move_to_destination(position, sorted_opponents[0])  # WARN: not proof in case of split
        return new_pos
