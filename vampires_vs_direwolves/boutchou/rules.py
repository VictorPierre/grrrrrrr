import functools
from random import randint
from time import sleep
from typing import Tuple, List

from boutchou import AbstractSafeAI

from common.logger import logger
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.map_helpers import (get_next_move_to_destination, get_distances_to_a_species,
                                         get_first_species_position_and_number)

WAIT_TIME = 1 * 0.11  # in seconds


class AbstractMoveRules:
    def __init__(self, game_map: AbstractGameMap, species: Species):
        self._game_map = game_map
        assert species in (Species.VAMPIRE, Species.WEREWOLF), f"Bad species moving: {species}"
        self._species = species


class PossibleMoves(AbstractMoveRules):
    """Class with rules to move from a position to a range of possible moves."""

    def get_possible_moves(self, position, *args, **kwargs) -> List[Tuple[int, int]]:
        return self._game_map.get_possible_moves(position, *args, *kwargs)

    def get_possible_moves_without_overcrowded_houses(self, position, *args, **kwargs) -> List[Tuple[int, int]]:
        possible_moves = self._game_map.get_possible_moves(position, *args, *kwargs)
        safe_possible_moves = []
        species_nb = self._game_map.get_cell_number(position)
        for move in possible_moves:
            spec, nb = self._game_map.get_cell_species_and_number(move)
            if spec is Species.HUMAN and nb >= species_nb:
                continue
            safe_possible_moves.append(move)
        return safe_possible_moves


class NextMoveRule(AbstractMoveRules):
    """Class with rules to move from a position to another"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._possible_moves = PossibleMoves(self._game_map, self._species)

    def no_move(self, position: Tuple[int, int], force_move=False) -> Tuple[int, int]:
        assert not force_move, "force_move attribute cannot be True for no_move method!"
        return position

    def safe_move(self, position, force_move=True, **_kwargs):
        possible_moves = self._possible_moves.get_possible_moves(position, force_move=force_move)
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
        elif method == "distance_then_number":
            sort_fn = lambda x: humans[x][1] * 10000 - self._game_map.get_cell_number(humans[x][0])
        elif method == "ratio":
            cd = params.get("coef_distance", 0)
            cn = params.get("coef_number", 0)
            sort_fn = lambda x: (humans[x][1] - cd) / (self._game_map.get_cell_number(humans[x][0]) + cn)
        elif method == "best_combo":
            raise NotImplementedError
        else:
            raise ValueError(method)
        return sorted(humans, key=sort_fn, reverse=False)

    def _move_to_human(self, position, method, **kwargs):
        sorted_humans = self._sort_humans(position, method=method, **kwargs)
        species_nb = self._game_map.get_cell_number(position)
        allowed_moves = self._possible_moves.get_possible_moves_without_overcrowded_houses(position)
        for human_pos in sorted_humans:
            if self._game_map.get_cell_number(human_pos) >= species_nb:
                continue
            new_pos = get_next_move_to_destination(position, human_pos)
            if new_pos not in allowed_moves:
                continue
            return new_pos
        return None

    def move_to_closest_human(self, position):
        return self._move_to_human(position, method="distance_then_number")

    def move_to_best_human(self, position, coef_number=0, coef_distance=0):
        return self._move_to_human(position, method="ratio", coef_number=coef_number, coef_distance=coef_distance)

    def move_to_closest_opponent(self, position):
        opponents = get_distances_to_a_species(position, self._game_map,
                                               species=Species.get_opposite_species(self._species))
        sorted_opponents = sorted(opponents, key=lambda x: opponents[x][1], reverse=False)
        if not sorted_opponents:
            logger.error(f"No more opponent against {self._species}!")
            return None
        new_pos = get_next_move_to_destination(position, sorted_opponents[0])  # WARN: not proof in case of split
        if new_pos not in self._possible_moves.get_possible_moves_without_overcrowded_houses(position):
            return None
        return new_pos


class RuleSequence(AbstractSafeAI):
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
