from abc import ABC, abstractmethod


class AbstractHeuristic(ABC):

    @abstractmethod
    def evaluate(self, game_map: GameMap, specie: Species):
        """ Evaluate the current map and return a number to score if it's in favour of the specie
        """
        pass
