# -*- coding: utf-8 -*-
"""
RÈGLES
Règle 1
Il faut au moins un mouvement
Règle 2
On ne peut déplacer que ses propres pions
Règle 3
Il faut avoir assez de pions sur une case pour satisfaire tous les mouvements partant de cette case
Règle 4
On ne peut se déplacer que sur une des 8 cases adjacentes
Règle 5
Une case ne peut pas se retrouver à la fois dans les cibles et les sources
Règle 6
Il faut au moins bouger un pion
"""
from collections import defaultdict
from typing import Tuple, List

from common.models import Species
from game_management.abstract_game_map import AbstractGameMap


def check_movements(movements: List[Tuple[int, int, int, int, int]], game_map: AbstractGameMap, species: Species):
    assert isinstance(movements, list)  # type
    # rule n°1
    assert len(movements) >= 1
    _starting_points, _ending_points = defaultdict(int), set()  # for rules

    for movement in movements:
        assert isinstance(movement, tuple)  # type
        assert len(movement) == 5  # format
        # table size respected
        assert 0 <= movement[0] < game_map.m  # 0 <= x < nb_columns
        assert 0 <= movement[1] < game_map.n  # 0 <= y < nb_lines
        assert 0 <= movement[3] < game_map.m  # 0 <= x < nb_columns
        assert 0 <= movement[4] < game_map.n  # 0 <= y < nb_lines
        # rule n°2
        assert game_map.get_cell_species((movement[0], movement[1])) is species
        # rule n°4
        assert -1 <= movement[0] - movement[3] <= 1
        assert -1 <= movement[1] - movement[4] <= 1
        _starting_points[(movement[0], movement[1])] += movement[2]
        _ending_points.add((movement[3], movement[4]))

    # rule n°5
    assert not (_starting_points.keys() & _ending_points)  # rule n°5
    # rule n°3 + rule n°6 + no movement of 0 person
    assert all(0 < nb <= game_map.get_cell_species_count(pos, species)
               for pos, nb in _starting_points.items())
