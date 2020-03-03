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

    def _sort_humans(self, position, method, **params):
        humans = get_distances_to_a_species(position, self._game_map, species=Species.HUMAN)
        if method == "distance":
            sort_fn = lambda x: humans[x][1]
        elif method == "ratio":
            cd = params.get("coef_distance", 0)
            cn = params.get("coef_number", 0)
            sort_fn = lambda x: (humans[x][1] - cd) / (self._game_map.get_cell_number(humans[x][0]) + cn)
        else:
            raise ValueError(method)
        return sorted(humans, key=sort_fn, reverse=False)

    def move_to_closest_human(self, position):
        sorted_humans = self._sort_humans(position, method="distance")
        species_nb = self._game_map.get_cell_number(position)
        for human_pos in sorted_humans:
            if self._game_map.get_cell_number(human_pos) >= species_nb:
                continue
            new_pos = get_next_move_to_destination(position, human_pos)
            if self._game_map.get_cell_species_count(new_pos, Species.HUMAN) >= species_nb:
                continue
            return new_pos
        return None

    def move_to_best_human(self, position, coef_number=0, coef_distance=0):
        sorted_humans = self._sort_humans(position, method="ratio",
                                          coef_number=coef_number, coef_distance=coef_distance)
        species_nb = self._game_map.get_cell_number(position)
        for human_pos in sorted_humans:
            if self._game_map.get_cell_number(human_pos) >= species_nb:
                continue
            new_pos = get_next_move_to_destination(position, human_pos)
            if self._game_map.get_cell_species_count(new_pos, Species.HUMAN) >= species_nb:
                continue
            return new_pos
        return None

    def move_to_closest_opponent(self, position):
        species = self._game_map.get_cell_species(position)
        assert species in (Species.VAMPIRE, Species.WEREWOLF), f"Bad species moving: {species}"
        opponents = get_distances_to_a_species(position, self._game_map, species=Species.get_opposite_species(species))
        sorted_opponents = sorted(opponents, key=lambda x: opponents[x][1], reverse=False)
        if not sorted_opponents:
            logger.error(f"No more opponent against {species}!")
            return None
        new_pos = get_next_move_to_destination(position, sorted_opponents[0])  # WARN: not proof in case of split
        return new_pos
