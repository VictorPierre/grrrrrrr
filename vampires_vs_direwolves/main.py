# -*- coding: utf-8 -*-
# using Python 3.6+
import sys

from game_management.game_manager import GameManager
from boutchou import Boutchou, HumanAI

"""
Main script, ready for a tournament.
`--human` argument is for tests only (battle against a human in an alternative web GUI)
"""

user_args = sys.argv[1:]
human = False


def print_help(return_value=0):
    print("Please specify host name and port:\n"
          "Example: python main.py 127.0.0.1 5555")
    exit(return_value)


if "--help" in user_args:
    print_help()

if not user_args:
    print("No arguments set. Using default configuration for server...")
    server_config = None
elif "--human" in user_args:
    human = True

else:
    try:
        server_config = {"host": user_args[0], "port": int(user_args[1])}
    except (ValueError, IndexError) as err:
        print(f"Bad arguments: {err}\n")
        print_help(1)


def main():
    game_manager = GameManager(server_config=server_config, ai_class=Boutchou) if not human \
        else GameManager(server_config=None, ai_class=HumanAI)
    game_manager.start()

    print("End of program")
    exit(0)


if __name__ == '__main__':
    main()
