# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Tuple, List

from common.models import Species
from game_management.abstract_game_map import AbstractGameMap


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
