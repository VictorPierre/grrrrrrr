# -*- coding: utf-8 -*-
from threading import Thread
from typing import List, Type

from common.logger import logger
from boutchou.abstract_ai import AbstractAI
from boutchou.default_ai import DefaultAI
from game_management.game_manager import GameManager
from game_management.game_master import GameMasterWorker


class GameComparator:
    def __init__(self, ais: List[Type[AbstractAI]]):
        self._ais = ais

    def test(self, nb_games: int = 2):
        game_master = GameMasterWorker(
            nb_players=2,
            max_rounds=200,
            max_nb_games=nb_games,
            auto_restart=int(0.5 * (len(self._ais) * (1 + len(self._ais)))) - 1
        )
        game_master.start()
        for i, ai_1 in enumerate(self._ais):
            for j in range(i, len(self._ais)):
                ai_2 = self._ais[j]

                player1 = Thread(target=GameManager(player_name=f"{ai_1.__name__}_1", ai_class=ai_1).start)
                player2 = Thread(target=GameManager(player_name=f"{ai_2.__name__}_2", ai_class=ai_2).start)
                player1.start()
                player2.start()
                player1.join()
                player2.join()
        game_master.join()
        return game_master.game_monitor


def multiple_games():
    ais = [DefaultAI]
    game_comparator = GameComparator(ais)
    game_monitor = game_comparator.test(10)
    print(game_monitor.global_summary)


if __name__ == '__main__':
    multiple_games()
