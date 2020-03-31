import numpy as np

from alphabeta.abstract_heuristic import AbstractHeuristic
from common.models import Species
from game_management.game_map import GameMap
from game_management.map_helpers import *


class NumberAndDistanceHeuristic(AbstractHeuristic):

    def __init__(self):
        super().__init__()
        self._num_factor = 10
        self._dist_factor = 0.1

    def evaluate(self, game_map: GameMap, specie: Species):

        # nb_vamp = np.sum(game_map.vampire_map)
        # nb_wolves = np.sum(game_map.werewolf_map)

        try:
            pos_vamp, nb_vamp = next(
                game_map.species_position_and_number_generator(Species.VAMPIRE))
        except StopIteration:
            # no more vampires on the map
            return -1e6 if specie == Species.VAMPIRE else 1e6
        try:
            pos_wolv, nb_wolves = next(
                game_map.species_position_and_number_generator(Species.WEREWOLF))
        except StopIteration:
            return 1e6 if specie == Species.VAMPIRE else -1e6

        dist_vamp_to_humans = get_distances_to_a_species(pos_vamp, game_map)
        dist_v = 0
        for key in dist_vamp_to_humans:
            # for each cell of human, add number of humans * distance to vamp cell
            if game_map.get_cell_species_count(key, Species.HUMAN) <= nb_vamp:
                dist_v += game_map.get_cell_species_count(key, Species.HUMAN) / \
                    dist_vamp_to_humans[key][1]

        dist_wolv_to_humans = get_distances_to_a_species(pos_wolv, game_map)

        dist_w = 0
        for key in dist_wolv_to_humans:
            # for each cell of human, add number of humans * distance to werewolf cell

            # count only for human cells with less humans than wolves so they can eat them
            if game_map.get_cell_species_count(key, Species.HUMAN) <= nb_wolves:
                dist_w += game_map.get_cell_species_count(key, Species.HUMAN) / \
                    dist_wolv_to_humans[key][1]
        #print('dist v', dist_v, 'dist w', dist_w)
        res = (nb_vamp - nb_wolves) * self._num_factor \
            + (dist_v - dist_w) * self._dist_factor - 0.001 * \
            get_direct_distance(pos_vamp, pos_wolv) * (nb_vamp - nb_wolves)

        return res if specie == Species.VAMPIRE else -res
