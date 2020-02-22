from abc import ABC, abstractmethod

from common.models import Species
from game_management.abstract_game_map import AbstractGameMap


class Abstract_Heuristic(ABC):

    @abstractmethod
    def evaluate(self, game_map: AbstractGameMap, specie: Species):
        """ Evaluate the current map and return a number to score if it's in favour of the specie  
        """
        pass
