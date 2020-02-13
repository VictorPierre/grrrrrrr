# -*- coding: utf-8 -*-
import enum
import numpy as np
from typing import Tuple

from common.exceptions import MapCorruptedException
from common.logger import logger


class DataType(enum.Enum):
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
    def from_cell_to_species_and_number(cls, cell: Tuple[int, int, int]):
        non_zero_indexes = np.nonzero(cell)
        if len(non_zero_indexes) != 1:
            err_msg = f"numpy.nonzero(cell) should be a tuple of length 1, found {non_zero_indexes} instead!"
            logger.error(err_msg)
            raise MapCorruptedException(err_msg)
        species_index = non_zero_indexes[0]
        if len(species_index) > 1:
            err_msg = f"More than one species in one cell ({cell})!"
            logger.error(err_msg)
            raise MapCorruptedException(err_msg)
        return (Species(species_index[0]), cell[species_index[0]]) if len(species_index) else (Species(3), 0)

    @classmethod
    def from_cell(cls, cell: Tuple[int, int, int]):
        return cls.from_cell_to_species_and_number(cell)[0]
