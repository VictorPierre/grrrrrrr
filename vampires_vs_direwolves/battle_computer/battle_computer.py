# -*- coding: utf-8 -*-
from typing import Tuple
from common.models import Species
from scipy.stats import binom


class BattleComputer():
    """Base class for AI"""


    def __init__(self, attacker: Tuple[Species, int], defender: Tuple[Species, int]):
        
        self.attacker_specie = attacker[0]
        self.attacker_count = attacker[1]
        self.defender_specie = defender[0]
        self.defender_count = defender[1]
        self.proba_attacker_wins = None
        
        self.__validate_battle()
        
        ##Check whether the issue of the battle is trivial or not
        if self.defender_specie is Species.HUMAN:
            self.__is_random_battle = self.attacker_count < self.defender_count ### TO CHECK : strict or not ?
        else:
            self.__is_random_battle = self.attacker_count < 1.5*self.defender_count ### TO CHECK : strict or not ?
        return

    def __validate_battle(self):
        """Ensure that the battle is possible and correct
        Raises:
            RuntimeError
        """
        #Defender and attacer are two different species
        if self.defender_specie == self.attacker_specie:
            raise RuntimeError
        #Attacker and defender are not NONE, and attacker is not HUMAN
        if self.attacker_specie == Species.NONE or self.attacker_specie == Species.HUMAN or self.defender_specie == Species.NONE:
            raise RuntimeError

    def get_proba(self):
        """Computes the probability of the event 'attacker wins'
        Returns:
            float -- probability of this event
        """
        if not self.__is_random_battle:
            self.proba_attacker_wins=1
        else:
            if self.attacker_count == self.defender_count:
                self.proba_attacker_wins=0.5
            elif self.attacker_count < self.defender_count:
                self.proba_attacker_wins = 0.5 * self.attacker_count / self.defender_count
            else: 
                self.proba_attacker_wins = self.attacker_count / self.defender_count - 0.5
        return self.proba_attacker_wins

    def get_esperance(self):
        """
        Returns:
            Tuple(attacker_results, defender_results)

            where attacker_results and defender_results are two tuples of the following type :
            (specie (type Specie), esperance in case of victory (type Float), proba of victory (type Float))

            example :
            ((WEREWOLF, 5.3, 0.6), (HUMAN, 3.1, 0.4))
        """
        ##Computes the probability
        if self.proba_attacker_wins == None:
            self.get_proba()
        if self.defender_specie is Species.HUMAN:
            attacker_results = (self.attacker_specie, self.proba_attacker_wins * (self.attacker_count+self.defender_count), self.proba_attacker_wins)
        else:
            attacker_results = (self.attacker_specie, self.proba_attacker_wins * self.attacker_count, self.proba_attacker_wins)
        defender_results = (self.defender_specie, (1 - self.proba_attacker_wins) * self.defender_count, 1 - self.proba_attacker_wins)
        return (attacker_results, defender_results)

    def get_all_probabilities(self):
        """return an array with all the possible issues, and their probabilities
        example :
            [(WEREWOLF, 1, 0.5), (VAMPIRE, 1, 0.5)]
        """
        ##Computes the probability
        if self.proba_attacker_wins == None:
            self.get_proba()

        ##Case of a certain victory
        if self.proba_attacker_wins==1:
            if self.defender_count is Species.HUMAN:
                return [(self.attacker_specie, self.attacker_count + self.defender_count, 1)]
            else:
                return [(self.attacker_specie, self.attacker_count, 1)]
        ##Case of a Random battle
        else:
            probabilities = []

            if self.defender_count is Species.HUMAN:
                n_attacker = self.attacker_count + self.defender_count
            else:
                n_attacker = self.attacker_count

            attacker_random_variable = binom(n_attacker, self.proba_attacker_wins)
            defender_random_variable = binom(self.defender_count, 1 - self.proba_attacker_wins)
            
            ##attacker victory
            for k in range(1, n_attacker+1):
                probabilities.append([self.attacker_specie, k, self.proba_attacker_wins * attacker_random_variable.pmf(k)])
            ##defender victory
            for k in range(1, self.defender_count+1):
                probabilities.append([self.defender_specie, k, (1 - self.proba_attacker_wins) * defender_random_variable.pmf(k)])
            ##no survivors
            probabilities.append([Species.NONE, 0, self.proba_attacker_wins * attacker_random_variable.pmf(0) +  (1 - self.proba_attacker_wins) * defender_random_variable.pmf(0)])

            return probabilities
        
if __name__=="__main__":
    b=BattleComputer((Species.WEREWOLF,2), (Species.VAMPIRE,2))

    print(b.get_proba())
    print(b.get_esperance())
    print(b.get_all_probabilities())