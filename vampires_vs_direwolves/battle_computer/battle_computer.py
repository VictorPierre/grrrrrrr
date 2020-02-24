# -*- coding: utf-8 -*-
from typing import Tuple
import numpy as np
from scipy.stats import binom

from common.exceptions import InvalidBattleException
from common.models import Species


class BattleComputer:
    """Base class for AI"""

    def __init__(self, attacker: Tuple[Species, int], defender: Tuple[Species, int]):

        self.attacker_specie = attacker[0]
        self.attacker_count = attacker[1]
        self.defender_specie = defender[0]
        self.defender_count = defender[1]
        self._proba_attacker_wins = None

        self.__validate_battle()

        # # Check whether the issue of the battle is trivial or not
        if self.defender_specie is Species.NONE or self.attacker_specie is self.defender_specie:  # No battle !
            self.__is_random_battle = False
        elif self.defender_specie is Species.HUMAN:
            self.__is_random_battle = self.attacker_count < self.defender_count  # strict inequality
        else:
            self.__is_random_battle = self.attacker_count < 1.5 * self.defender_count  # strict inequality

    def __validate_battle(self):
        """Ensure that the battle is possible and correct
        Raises:
            InvalidBattleException
        """
        # Attacker and defender are not NONE, and attacker is not HUMAN
        if self.attacker_specie in (Species.NONE, Species.HUMAN):
            raise InvalidBattleException(f"Attacker is an invalid species: {self.attacker_specie}")

    @property
    def proba_attacker_wins(self):
        """Returns the probability of the event 'attacker wins'

        :return: float -- probability of this event
        """
        if self._proba_attacker_wins is None:
            self._compute_proba_attacker_wins()
        return self._proba_attacker_wins

    def _compute_proba_attacker_wins(self):
        """Computes the probability of the event 'attacker wins' and set it to self._proba_attacker_wins

        Specifications:
            Soit E1 et E2 les effectifs respectifs des deux espèces, E1 étant l’effectif de l’espèce attaquante :
            - Si E1=E2, alors P = 0,5 ;
            - Si E1<E2, alors 𝑃 = E1 /(2×E2) ;
            - Sinon P = E1/E2 − 0,5.
            La probabilité que E1 remporte la victoire est donnée par P.
        Returns:
            None
        """
        if not self.__is_random_battle:
            self._proba_attacker_wins = 1
        elif self.attacker_count == self.defender_count:
            self._proba_attacker_wins = 0.5
        elif self.attacker_count < self.defender_count:
            self._proba_attacker_wins = 0.5 * self.attacker_count / self.defender_count
        else:
            self._proba_attacker_wins = self.attacker_count / self.defender_count - 0.5

    def get_esperance(self):
        """
        Returns:
            Tuple(attacker_results, defender_results)

            where attacker_results and defender_results are two tuples of the following type :
            (specie (type Specie), expectation in case of victory (type Float), proba of victory (type Float))

            example :
            ((WEREWOLF, 5.3, 0.6), (HUMAN, 3.1, 0.4))
        """
        # Fusion of two groups of the same species
        if self.defender_specie is self.attacker_specie:
            return (self.attacker_specie, self.attacker_count, 1), (self.defender_specie, self.defender_count, 1)

        # Battle
        if self.defender_specie is Species.HUMAN:
            attacker_results = (self.attacker_specie,
                                self.proba_attacker_wins * (self.attacker_count + self.defender_count),
                                self.proba_attacker_wins)
        else:
            attacker_results = (self.attacker_specie,
                                self.proba_attacker_wins * self.attacker_count,
                                self.proba_attacker_wins)
        defender_results = (self.defender_specie,
                            (1 - self.proba_attacker_wins) * self.defender_count,
                            1 - self.proba_attacker_wins)
        return attacker_results, defender_results

    def compute_one_battle_result(self) -> Tuple[Species, int]:
        """Returns a possible battle result, using a Bernoulli law (victory) and a binomial law (survivors)"""
        # Fasten the results for trivial battles:
        if self.attacker_specie is self.defender_specie:
            return self.attacker_specie, self.attacker_count + self.defender_count
        if self.defender_specie is Species.NONE:
            return self.attacker_specie, self.attacker_count
        if self.proba_attacker_wins == 1:
            if self.defender_specie is Species.HUMAN:
                return self.attacker_specie, self.attacker_count + self.defender_count
            return self.attacker_specie, self.attacker_count
        # Non trivial battles
        victory = np.random.binomial(n=1, p=self.proba_attacker_wins)
        expectation = self.get_esperance()[1 - victory][1]
        nb_survivors = np.random.binomial(n=expectation / self.proba_attacker_wins, p=self.proba_attacker_wins)
        if not nb_survivors:
            winning_species = Species.NONE
        elif victory:
            winning_species = self.attacker_specie
        else:
            winning_species = self.defender_specie
        return winning_species, nb_survivors

    def get_all_probabilities(self):
        """return an array with all the possible issues, and their probabilities
        example :
            [(WEREWOLF, 1, 0.5), (VAMPIRE, 1, 0.5)]
        """
        # # Case of a certain victory
        if self.proba_attacker_wins == 1:
            if self.defender_count is Species.HUMAN or self.attacker_specie is self.defender_specie:
                return [(self.attacker_specie, self.attacker_count + self.defender_count, 1)]
            else:
                return [(self.attacker_specie, self.attacker_count, 1)]

        # # Case of a Random battle
        probabilities = []

        if self.defender_count is Species.HUMAN:
            n_attacker = self.attacker_count + self.defender_count
        else:
            n_attacker = self.attacker_count

        attacker_random_variable = binom(n_attacker, self.proba_attacker_wins)
        defender_random_variable = binom(self.defender_count, 1 - self.proba_attacker_wins)

        # # attacker victory
        for k in range(1, n_attacker + 1):
            probabilities.append(
                [self.attacker_specie, k, self.proba_attacker_wins * attacker_random_variable.pmf(k)])
        # # defender victory
        for k in range(1, self.defender_count + 1):
            probabilities.append(
                [self.defender_specie, k, (1 - self.proba_attacker_wins) * defender_random_variable.pmf(k)])
        # # no survivors
        probabilities.append([Species.NONE, 0, self.proba_attacker_wins * attacker_random_variable.pmf(0) + (
                1 - self.proba_attacker_wins) * defender_random_variable.pmf(0)])

        return probabilities


if __name__ == "__main__":
    b = BattleComputer((Species.WEREWOLF, 2), (Species.VAMPIRE, 2))

    print(b.proba_attacker_wins)
    print(b.get_esperance())
    probabilities = b.get_all_probabilities()
    print(probabilities)

    # Test of compute_one_battle_result method
    print(b.compute_one_battle_result())
    possibilities = [tuple(ele[:2]) for ele in probabilities]
    assert all(b.compute_one_battle_result() in possibilities for _ in range(10000))
