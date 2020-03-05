# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Tuple, List, Optional

from boutchou.rules import NextMoveRule
from common.exceptions import SpeciesExtinctionException
from common.logger import logger
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.map_helpers import get_first_species_position_and_number


class AbstractAI(ABC):
    """Base class for AI"""

    def __init__(self):
        # noinspection PyTypeChecker
        self._map: AbstractGameMap = None
        self._species: Species = Species.NONE

    def load_map(self, game_map: AbstractGameMap) -> None:
        self._map = game_map

    def load_species(self, species: Species) -> None:
        self._species = species

    @abstractmethod
    def generate_move(self) -> List[Tuple[int, int, int, int, int]]:
        pass


class AbstractSafeAI(AbstractAI, ABC):

    @abstractmethod
    def _generate_move(self) -> Optional[List[Tuple[int, int, int, int, int]]]:
        return None

    def generate_move(self) -> List[Tuple[int, int, int, int, int]]:
        return self._generate_move() or self.generate_safe_move()

    def generate_safe_move(self):
        """Generate an always-safe move (in the sense of game rules)"""
        old_position, number = get_first_species_position_and_number(self._map, self._species)
        new_position = NextMoveRule(self._map, self._species).safe_move(old_position)
        logger.debug(f"Safe move: {new_position}")
        return [(*old_position, number, *new_position)]
