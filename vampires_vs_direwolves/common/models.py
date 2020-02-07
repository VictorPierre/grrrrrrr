# -*- coding: utf-8 -*-
import enum
import numpy as np
from typing import Tuple

from exceptions import MapCorruptedException


class Type(enum.Enum):
    STR = 0
    INT = 1


class Command(enum.Enum):
    SET = "set"
    HUM = "hum"
    HME = "hme"
    MAP = "map"
    UPD = "upd"
    END = "end"
    BYE = "bye"


class Species(enum.Enum):
    HUMAN = 0
    VAMPIRE = 1
    WEREWOLF = 2
    NONE = 3

    @classmethod
    def from_cell(cls, cell: Tuple[int, int, int]):
        non_zero_indexes = np.nonzero(cell)
        if len(non_zero_indexes) > 1:
            raise MapCorruptedException(f"More than one species in one cell ({cell})!")
        return Species(non_zero_indexes[0]) if non_zero_indexes else Species(3)
