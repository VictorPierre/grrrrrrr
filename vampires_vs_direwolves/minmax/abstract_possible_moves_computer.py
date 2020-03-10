from game_management.abstract_game_map import AbstractGameMap


class AbstractPossibleMovesComputer:

    @staticmethod
    def move_computer(game_map: AbstractGameMap, species):
        possible_moves = game_map.get_possible_moves(game_map.find_species_position(species)[0])
        # TODO
        pass
