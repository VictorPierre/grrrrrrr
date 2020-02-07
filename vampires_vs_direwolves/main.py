# -*- coding: utf-8 -*-
# using Python 3.6+
import sys

user_args = sys.argv[1:]


def print_help(return_value=0):
    print("Please specify host name and port:\n"
          "Example: python main.py 127.0.0.1 5555")
    exit(return_value)


if "--help" in user_args:
    print_help()

if not user_args:
    print("No arguments set. Using default configuration for server...")
    server_config = None
else:
    try:
        server_config = {"host": user_args[0], "port": int(user_args[1])}
    except (ValueError, IndexError) as err:
        print(f"Bad arguments: {err}\n")
        print_help(1)


def main():
    from game_management.game_manager import GameManager

    game_manager = GameManager(server_config=server_config)
    game_manager.start()

    print("End of program")
    exit(0)


main()
