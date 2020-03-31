from random import randint, shuffle
from typing import Tuple, List

from common.logger import logger
from common.models import Species
from game_management.abstract_game_map import AbstractGameMap
from game_management.map_helpers import (get_next_move_to_destination, get_distances_to_a_species, get_direct_distance)


class AbstractMoveRules:
    def __init__(self, game_map: AbstractGameMap, species: Species):
        self._game_map = game_map
        assert species in (Species.VAMPIRE, Species.WEREWOLF), f"Bad species moving: {species}"
        self._species = species


class PossibleMoves(AbstractMoveRules):
    """Class with rules to move from a position to a range of possible moves."""

    def get_possible_moves(self, position, *args, **kwargs) -> List[Tuple[int, int]]:
        return self._game_map.get_possible_moves(position, *args, **kwargs)

    def get_possible_moves_without_overcrowded_houses(self, position, *args, **kwargs) -> List[Tuple[int, int]]:
        possible_moves = self._game_map.get_possible_moves(position, *args, **kwargs)
        safe_possible_moves = []
        species_nb = self._game_map.get_cell_number(position)
        for move in possible_moves:
            spec, nb = self._game_map.get_cell_species_and_number(move)
            if spec is Species.HUMAN and nb >= species_nb:
                continue
            safe_possible_moves.append(move)
        return safe_possible_moves


class NextMoveRule(AbstractMoveRules):
    """Class with rules to move from a position to another"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._possible_moves = PossibleMoves(self._game_map, self._species)

    def no_move(self, position: Tuple[int, int], force_move=False) -> Tuple[int, int]:
        assert not force_move, "force_move attribute cannot be True for no_move method!"
        return position

    def safe_move(self, position, force_move=True, **_kwargs):
        possible_moves = self._possible_moves.get_possible_moves(position, force_move=force_move)
        assert len(possible_moves), f"No possible move from {position}! Map size may be too small."
        return possible_moves[0]

    def random_move(self, position: Tuple[int, int], force_move=True) -> Tuple[int, int]:
        possible_moves = self._game_map.get_possible_moves(position, force_move=force_move)
        rand_ind = randint(0, len(possible_moves) - 1)
        new_pos = possible_moves[rand_ind]
        return new_pos

    def _sort_humans(self, position, method, **params):
        humans = get_distances_to_a_species(position, self._game_map, species=Species.HUMAN)
        if method == "distance":
            sort_fn = lambda x: humans[x][1]
        elif method == "distance_then_number":
            sort_fn = lambda x: humans[x][1] * 10000 - self._game_map.get_cell_number(humans[x][0])
        elif method == "ratio":
            cd = params.get("coef_distance", 0)
            cn = params.get("coef_number", 0)
            sort_fn = lambda x: (humans[x][1] - cd) / (self._game_map.get_cell_number(humans[x][0]) + cn)
        elif method == "best_combo":
            raise NotImplementedError
        else:
            raise ValueError(method)
        return sorted(humans, key=sort_fn, reverse=False)

    def _move_to_human(self, position, method, **kwargs):
        sorted_humans = self._sort_humans(position, method=method, **kwargs)
        species_nb = self._game_map.get_cell_number(position)
        allowed_moves = self._possible_moves.get_possible_moves_without_overcrowded_houses(position)
        for human_pos in sorted_humans:
            if self._game_map.get_cell_number(human_pos) >= species_nb:
                continue
            new_pos = get_next_move_to_destination(position, human_pos)
            if new_pos not in allowed_moves:
                continue
            return new_pos
        return None

    def move_to_closest_human(self, position):
        return self._move_to_human(position, method="distance_then_number")

    def move_to_best_human(self, position, coef_number=0, coef_distance=0):
        return self._move_to_human(position, method="ratio", coef_number=coef_number, coef_distance=coef_distance)

    def move_to_closest_opponent(self, position):
        opponents = get_distances_to_a_species(position, self._game_map,
                                               species=Species.get_opposite_species(self._species))
        sorted_opponents = sorted(opponents, key=lambda x: opponents[x][1], reverse=False)
        if not sorted_opponents:
            logger.error(f"No more opponent against {self._species}!")
            return None
        new_pos = get_next_move_to_destination(position, sorted_opponents[0])  # WARN: not proof in case of split
        if new_pos not in self._possible_moves.get_possible_moves_without_overcrowded_houses(position):
            return None
        return new_pos

    def escape_direct_threat(self, position, **params):
        ##TO FIX: tendance à se faire piéger sur les bords
    
        own_number = self._game_map.get_cell_species_count(position, self._species)
        opponents = get_distances_to_a_species(position, self._game_map, species=Species.get_opposite_species(self._species))
        ##direct threats are opponents that are at a distance of 1 and more than 1.5x the own_number
        direct_threats = list(filter(lambda x: opponents[x][1]==1 & opponents[x][2]>=1.5*own_number, opponents))

        if len(direct_threats)==0:
            return None
        else:
            possible_moves = self._game_map.get_possible_moves(position, force_move=True)
            ##test all possible moves, and chose the first one that is safe
            for move in shuffle(possible_moves):
                if move not in direct_threats:
                    opponents = get_distances_to_a_species(move, self._game_map, species=Species.get_opposite_species(self._species))
                    new_threats = list(filter(lambda x: opponents[x][1]<=1 & opponents[x][2]>=0.5*own_number, opponents))
                    if len(new_threats)==0:
                        return move

    ##helper
    def _list_subsets(self, seq):
        p = []
        i, imax = 0, 2**len(seq)-1
        while i <= imax:
            s = []
            j, jmax = 0, len(seq)-1
            while j <= jmax:
                if (i>>j)&1 == 1:
                    s.append(seq[j])
                j += 1
            p.append(s)
            i += 1 
        return p

    def move_to_humans_with_split(self, position, **params):
        own_number = self._game_map.get_cell_species_count(position, self._species)
        opponents = get_distances_to_a_species(position, self._game_map, species=Species.get_opposite_species(self._species))
        humans = get_distances_to_a_species(position, self._game_map, species=Species.HUMAN)

        ##search humans that are not reachable for the opponent
        accessible_humans = list(humans.keys()) ##TO DO

        ##list subsets that are reachable (inferiory)
        possible_humans_subset = self._list_subsets(accessible_humans)
        possible_humans_subset = list(filter(lambda subset: len(subset)+sum([humans[key][2] for key in subset])<=own_number, possible_humans_subset))

        ##chose the best split strategy
        target_humans = max(possible_humans_subset, key=lambda subset: sum([humans[key][2]/humans[key][1] for key in subset]))

        ##generate moves toward the target humans, and repart all ressources
        moves = []
        ressources_to_dispach = own_number-len(target_humans)-sum([humans[key][2] for key in target_humans])

        for target in target_humans:
            n = humans[target][2]+1+ressources_to_dispach//len(target_humans)
            new_position = get_next_move_to_destination(position, target)
            moves.append((new_position,n))
        
        
        if len(moves)>0:
            ##assign the rest of ressources to the forst group
            moves[0]=(moves[0][0],moves[0][1]+ressources_to_dispach%len(target_humans))
            return moves
        return None

    def move_to_friends(self, position,**params):
        return None

    def _get_accessible_positions(self, position_attacker, position_enemy):
        """Get accessible positions of enemy if chased by attacker. It's position_attacker turn."""
        # todo: optimize algorithm with geometrical considerations
        distance = get_direct_distance(position_attacker, position_enemy)
        if distance == 1:
            return []
        accessible_positions = []
        for position in self._game_map.positions:
            # todo: to be optimized
            if get_direct_distance(position, position_enemy) < get_direct_distance(position, position_attacker):
                accessible_positions.append(position)
        return accessible_positions

    def move_to_opponent_if_blocked(self, position):
        """Move to opponent if you are certain to win (modulo some approximations)"""
        own_number = self._game_map.get_cell_species_count(position, self._species)
        enemy_species = Species.get_opposite_species(self._species)
        enemies = self._game_map.find_species_position_and_number(enemy_species)
        for enemy_position, enemy_number in enemies:
            if enemy_number * 1.5 >= own_number:  # too risky to attack
                continue
            potential_increased_number = enemy_number
            for potential_backup_position in self._get_accessible_positions(position, enemy_position):
                pot_sp, pot_nb = self._game_map.get_cell_species_and_number(potential_backup_position)
                if pot_sp is Species.HUMAN and enemy_number > pot_nb and True:
                    potential_increased_number += pot_nb
                if pot_sp is enemy_species:
                    potential_increased_number += pot_nb
                # todo: also take into account own species blocked and that could be converted by the enemy
                if potential_increased_number * 1.5 >= own_number:
                    break
            if potential_increased_number * 1.5 < own_number:  # enemy can not grow enough to win
                new_pos = get_next_move_to_destination(position, enemy_position)
                if new_pos in self._possible_moves.get_possible_moves_without_overcrowded_houses(position):
                    print("Move to opponent if blocked used!")
                    return new_pos
        return None
