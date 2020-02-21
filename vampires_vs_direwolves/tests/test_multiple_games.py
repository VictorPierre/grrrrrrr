# -*- coding: utf-8 -*-
from threading import Thread

from boutchou.default_ai import DefaultAI
from common.logger import logger
from game_management.game_manager import GameManager
from server_connection.game_server import GameServer


def multiple_games():
    game_server = Thread(target=GameServer(max_nb_games=5, show_map=False).run)
    game_server.start()

    player1 = Thread(target=GameManager(player_name="Boutchou", ai_class=DefaultAI).start)
    player2 = Thread(target=GameManager(player_name="Boss", ai_class=DefaultAI).start)
    player1.start()
    player2.start()
    player1.join()
    player2.join()

    game_server.join()
    logger.debug("Game server closed")


if __name__ == '__main__':
    multiple_games()
