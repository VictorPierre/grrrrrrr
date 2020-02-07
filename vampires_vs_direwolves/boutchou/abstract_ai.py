# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Tuple, List

from common.models import Species
from game_management.game_map import GameMap


class AbstractAI(ABC):
    """Base class for AI"""
    def __init__(self):
        self._map: GameMap = None
        self._species: Species = None

    def load_map(self, game_map: GameMap) -> None:
        self._map = game_map

    def load_species(self, species: Species) -> None:
        self._species = species

    @abstractmethod
    def generate_move(self) -> List[Tuple[int, int, int, int, int]]:
        pass
