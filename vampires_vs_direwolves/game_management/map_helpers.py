# -*- coding: utf-8 -*-
from typing import Tuple, Dict, List, Union

from common.models import Species
from game_management.abstract_game_map import AbstractGameMap


def get_direct_distance(position_1: Tuple[int, int], position_2: Tuple[int, int]):
    x1, y1 = position_1
    x2, y2 = position_2
    diagonal_distance = min(abs(x2 - x1), abs(y2 - y1))
    x_distance = abs(x2 - x1) - diagonal_distance
    y_distance = abs(y2 - y1) - diagonal_distance
    total_distance = diagonal_distance + x_distance + y_distance
    return total_distance


def get_distances_to_a_species(position: Tuple[int, int], game_map: AbstractGameMap,
                               species=Species.HUMAN) -> Dict[Tuple[int, int], Tuple[Tuple[int, int], int]]:
    species_positions = game_map.find_species_position(species)
    res = {}
    for species_position in species_positions:
        res[species_position] = (position, get_direct_distance(position, species_position))
    return res


def get_distances_between_two_species(game_map: AbstractGameMap, species_1: Species,
                                      species_2=Species.HUMAN) -> Dict[Tuple[int, int], Tuple[Tuple[int, int], int]]:
    """

    :param game_map:
    :param species_1:
    :param species_2:
    :return: {pos_specie_2: (pos_closest_specie_1, distance), ...}
    """
    species_1_pos = game_map.find_species_position(species_1)

    if not species_1:
        return {}

    # todo: optimize algorithm
    for i, pos_1 in enumerate(species_1_pos):
        if not i:
            distances = get_distances_to_a_species(pos_1, game_map, species_2)
        else:
            tmp_distances = get_distances_to_a_species(pos_1, game_map, species_2)
            for pos_2, (_pos, distance) in distances.items():
                tmp_distance = tmp_distances[pos_2][1]
                if tmp_distance < distance:
                    distances[pos_2] = (pos_1, tmp_distance)
    return distances


def _get_next_coord_to_destination(initial_coord, destination_coord):
    if destination_coord - initial_coord:
        return int((destination_coord - initial_coord) / abs(destination_coord - initial_coord))
    else:
        return 0


def get_next_move_to_destination(initial_position, destination):
    shift_x = _get_next_coord_to_destination(initial_position[0], destination[0])
    shift_y = _get_next_coord_to_destination(initial_position[1], destination[1])
    return initial_position[0] + shift_x, initial_position[1] + shift_y


if __name__ == '__main__':
    # Tests for get_direct_distance function
    assert get_direct_distance((0, 0), (0, 0)) == 0
    assert get_direct_distance((0, 2), (0, 0)) == 2
    assert get_direct_distance((2, 0), (0, 0)) == 2
    assert get_direct_distance((2, 2), (0, 0)) == 2
    assert get_direct_distance((3, 2), (0, 0)) == 3
    assert get_direct_distance((2, 3), (0, 0)) == 3
    assert get_direct_distance((0, 0), (2, 3)) == 3


    # Tests for get_distances_to_a_species function
    class MockMap(AbstractGameMap):
        def load_map(self, n: int, m: int):
            pass

        def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
            pass

        def get_cell_species(self, position: Tuple[int, int]) -> Species:
            pass

        def get_cell_species_and_number(self, position: Tuple[int, int]) -> Tuple[Species, int]:
            pass

        def get_cell_species_count(self, position: Tuple[int, int], species: Union[Species, int]) -> int:
            pass

        def find_species_position(self, species: Species) -> List[Tuple[int, int]]:
            if species is Species.HUMAN:
                return [(1, 2), (3, 3)]
            else:
                return [(0, 0), (2, 1)]


    assert get_distances_to_a_species((0, 0), MockMap(), Species.HUMAN) == {(1, 2): ((0, 0), 2), (3, 3): ((0, 0), 3)}

    # Tests for get_distances_between_two_species
    assert get_distances_between_two_species(MockMap(), Species.VAMPIRE, Species.HUMAN) == {(1, 2): ((2, 1), 1),
                                                                                            (3, 3): ((2, 1), 2)}

    # Tests for _get_next_coord_to_destination
    assert _get_next_coord_to_destination(1, 4) == 1
    assert _get_next_coord_to_destination(5, 2) == -1
    assert _get_next_coord_to_destination(2, 2) == 0
