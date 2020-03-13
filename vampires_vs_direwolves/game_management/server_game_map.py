from typing import Any, Dict, List, Tuple

from game_management.abstract_game_map_with_visualizer import \
    AbstractGameMapWithVisualizer
from game_management.game_map import GameMap


class ServerGameMap(GameMap, AbstractGameMapWithVisualizer):
    def __init__(self, game_monitor=None):
        super().__init__()
        self._game_monitor = game_monitor

    def update(self, ls_updates: List[Tuple[int, int, int, int, int]]):
        super().update(ls_updates)
        self._map_viewer.monitor(self._game_monitor)
