from common.logger import logger
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from alphabeta.abstract_heuristic import AbstractHeuristic
from game_management.map_helpers import get_distances_between_two_species


class SpeciesRatioHeuristic(AbstractHeuristic):
    """nombre de l'espèce / nombre de l'espèce ennemie"""
    def evaluate(self, game_map: AbstractGameMap, specie: Species):
        heuristic = game_map.count_species(specie) / game_map.count_species(Species.get_opposite_species(specie))
        logger.debug(f"Heuristic SpeciesRatioHeuristic: {heuristic}")
        return heuristic


class ExpectationHeuristic(AbstractHeuristic):
    """Somme(Nombre d'humains à convertir / distance à parcourir) / (nombre d'ennemis * 100)"""
    def evaluate(self, game_map: AbstractGameMap, specie: Species):
        enemies_nb = game_map.count_species(Species.get_opposite_species(specie)) * 100  # most important

        distances = get_distances_between_two_species(game_map, specie, Species.HUMAN, only_if_certain_victory=True)
        ratios = [nb_humans_to_convert / distance for _pos, distance, nb_humans_to_convert in distances.values()]

        heuristic = sum(ratios) / enemies_nb
        logger.debug(f"Heuristic ExpectationHeuristic: {heuristic}\nRatios: {ratios}")
        return heuristic

