# -*- coding: utf-8 -*-
from threading import Thread
from typing import List, Type
import os

from common.logger import logger
from boutchou import *
from game_management.game_manager import GameManager
from game_management.game_master import GameMasterWorker
from game_management.map_viewer import MapViewer


class GameComparator:
    def __init__(self, ais: List[Type[AbstractAI]], map_paths: List[str] = None):
        self._ais = ais
        self._map_paths = map_paths or [""]
        logger.info(f"AIs: {[ai.__name__ for ai in self._ais]}\nMaps: {map_paths}")

    def test(self, nb_games: int = 2, only_different_ais=False, show_map=False):
        MapViewer().set_visible(show_map)
        game_master = GameMasterWorker(
            nb_players=2,
            max_rounds=200,
            max_nb_games=nb_games,
            auto_restart=len(self._map_paths)*int(0.5 * (len(self._ais) * (1 + len(self._ais) - 2 * int(only_different_ais)))) - 1
        )
        game_master.change_map_path(self._map_paths[0])
        game_master.start()

        def launch_games():
            for map_path in self._map_paths:
                game_master.change_map_path(map_path)
                for i, ai_1 in enumerate(self._ais):
                    for j in range(i + int(only_different_ais), len(self._ais)):
                        ai_2 = self._ais[j]

                        player1 = Thread(target=GameManager(player_name=f"{ai_1.__name__}_1", ai_class=ai_1).start)
                        player2 = Thread(target=GameManager(player_name=f"{ai_2.__name__}_2", ai_class=ai_2).start)
                        player1.start()
                        player2.start()
                        player1.join()
                        player2.join()

        players_thread = Thread(target=launch_games)
        players_thread.start()
        MapViewer().mainloop()
        players_thread.join()
        game_master.stop()
        return game_master.game_monitor


def multiple_games():
    # Configure your tests here:
    ais = [AlphaBetaAI, ExpertAI]
    print(os.getcwd())
    map_paths = ["tests/test_maps/" + ele for ele in os.listdir("tests/test_maps") if ele.endswith(".xml")]
    game_comparator = GameComparator(ais, map_paths)
    game_monitor = game_comparator.test(nb_games=20, only_different_ais=True, show_map=True)
    logger.info(game_monitor)


if __name__ == '__main__':
    multiple_games()
