from threading import Thread
from time import sleep

from boutchou import *
from common.logger import logger
from game_management.game_manager import GameManager
from game_management.game_master import GameMasterWorker
from game_management.map_viewer import MapViewer

"""
Script to launch a battle between two AIs with the alternative game master.
If `MapViewer().set_visible(True)`, an alternative visualizer will show the battle.
"""

if __name__ == '__main__':

    # Launch server
    MapViewer().set_visible(False)
    game_master = GameMasterWorker(
        nb_players=2, max_rounds=100, max_nb_games=2, auto_restart=0)
    game_master.start()
    sleep(1)

    # Create players
    player1 = Thread(target=GameManager(
        player_name="Boutchou", ai_class=Boutchou).start)
    player2 = Thread(target=GameManager(
        player_name="Boss", ai_class=MoveToHumanOrMoveToOpponentIfBetter).start)
    player1.start()
    player2.start()
    MapViewer().mainloop()

    # # End of game
    player1.join()
    player2.join()
    game_master.join()
    logger.info(f"Game summary: {game_master.game_monitor}")
    logger.info("END OF GAME MASTER / SERVER")
