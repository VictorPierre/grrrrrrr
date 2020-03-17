from abc import ABC, abstractmethod

import numpy as np
import torch
import torch.nn as nn
from torch.autograd import grad

from common.models import Species
from game_management.game_map import GameMap
from game_management.map_helpers import *


class AbstractHeuristic(ABC):

    @abstractmethod
    def evaluate(self, game_map: GameMap, specie: Species):
        """ Evaluate the current map and return a number to score if it's in favour of the specie
        """
        pass


class NumberAndDistanceHeuristic(AbstractHeuristic):

    def __init__(self):
        super().__init__()
        self._num_factor = 10
        self._dist_factor = 0.01

    def evaluate(self, game_map: GameMap, specie: Species):

        nb_vamp = np.sum(game_map._vampire_map)
        nb_wolves = np.sum(game_map._werewolf_map)

        try:
            pos_vamp = next(
                game_map.species_position_generator(Species.VAMPIRE))
        except StopIteration:
            # no more vampires on the map
            return -1e6 if specie == Species.VAMPIRE else 1e6
        try:
            pos_wolv = next(
                game_map.species_position_generator(Species.WEREWOLF))
        except StopIteration:
            return 1e6 if specie == Species.VAMPIRE else -1e6

        dist_vamp_to_humans = get_distances_to_a_species(pos_vamp, game_map)
        dist_v = 0
        for key in dist_vamp_to_humans:
            # for each cell of human, add number of humans * distance to vamp cell
            dist_v += game_map.get_cell_species_count(key, Species.HUMAN) * \
                dist_vamp_to_humans[key][1]

        dist_wolv_to_humans = get_distances_to_a_species(pos_wolv, game_map)

        dist_w = 0
        for key in dist_wolv_to_humans:
            # for each cell of human, add number of humans * distance to werewolf cell
            dist_w += game_map.get_cell_species_count(key, Species.HUMAN) * \
                dist_wolv_to_humans[key][1]

        res = (nb_vamp - nb_wolves) * self._num_factor \
            + (dist_w - dist_v) * self._dist_factor - 0.001 * \
            get_direct_distance(pos_vamp, pos_wolv) * (nb_vamp - nb_wolves)

        return res if specie == Species.VAMPIRE else -res
