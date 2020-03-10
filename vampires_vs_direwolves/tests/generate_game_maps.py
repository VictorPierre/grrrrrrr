# -*- coding: utf-8 -*-

import os
import sys
from random import randint

from game_management.abstract_game_map import AbstractGameMap
from common.exceptions import GameMapOverPopulated


if __name__ == '__main__':
    assert sys.platform == "win32", "Windows is required to run this script"
    curr_dir = os.path.basename(os.getcwd())
    if curr_dir == "grrrrrrr":
        script_path = r"map_generator\MapGenerator.exe"
        map_path = "vampires_vs_werewolves\\tests\\test_maps\\"
    elif curr_dir == "vampires_vs_werewolves":
        script_path = r"..\map_generator/MapGenerator.exe"
        map_path = "tests\\test_maps\\"
    elif curr_dir == "tests":
        script_path = r"..\..\map_generator\MapGenerator.exe"
        map_path = "test_maps\\"
    else:
        raise FileNotFoundError

    os.makedirs(map_path, exist_ok=True)
    for i in range(20):
        n = randint(5, 30)
        m = randint(5, 30)
        nb_humans = randint(0, int(min(0.5*(n*m - 2), 30)))
        output_path = map_path + f"testmap{i}-{n}x{m}_({nb_humans}h).xml"
        cmd = f"{script_path} {n} {m} {nb_humans} {output_path}"
        print(cmd)
        os.system(cmd)

        try:
            AbstractGameMap.get_map_param_from_file(output_path)
        except GameMapOverPopulated as err:
            print(err)
            os.remove(output_path)
