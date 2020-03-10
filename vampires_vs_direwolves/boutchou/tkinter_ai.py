# -*- coding: utf-8 -*-
from typing import Tuple, List

from common.logger import logger
from boutchou.abstract_ai import AbstractAI
from common.exceptions import BaseGameException
from game_management.map_viewer import MapViewer


class InterfaceError(BaseGameException):
    pass


class TkinterHumanAI(AbstractAI):
    def generate_move(self) -> List[Tuple[int, int, int, int, int]]:
        map_viewer = MapViewer()
        if not map_viewer.is_visible:
            raise InterfaceError("Map Viewer not visible!")
        moves = map_viewer.get_user_moves(self._species)
        return moves
