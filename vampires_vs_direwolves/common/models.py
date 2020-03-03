# -*- coding: utf-8 -*-
from __future__ import annotations
import enum
import numpy as np
from typing import Tuple

from common.exceptions import MapCorruptedException, IncorrectSpeciesException, IncorrectCommandException
from common.logger import logger


class DataType(enum.Enum):
    STR = 0
    INT = 1


class _Command(enum.Enum):

    @classmethod
    def from_string(cls, message: str) -> _Command:
        try:
            command = cls[message]
        except KeyError as _err:
            logger.error(f"Error: got an invalid command: {message}")
            raise IncorrectCommandException(_err)
        return command


class Command(_Command):
    SET = "set"
    HUM = "hum"
    HME = "hme"
    MAP = "map"
    UPD = "upd"
    END = "end"
    BYE = "bye"


class PlayerCommand(_Command):
    NME = "nme"
    MOV = "mov"


class Species(enum.Enum):
    HUMAN = 0
    VAMPIRE = 1
    WEREWOLF = 2
    NONE = 3

    def __repr__(self):
        return self.name

    @classmethod
    def from_cell_to_species_and_number(cls, cell: Tuple[int, int, int]) -> (Species, int):
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
    def from_cell(cls, cell: Tuple[int, int, int]) -> Species:
        return cls.from_cell_to_species_and_number(cell)[0]

    def to_cell(self, position: Tuple[int, int], number: int) -> Tuple[int, int, int, int, int]:
        assert number >= 0
        cell = [*position, 0, 0, 0]
        if self is not Species.NONE:
            cell[2 + self.value] = number
        return tuple(cell)

    @classmethod
    def from_xml_tag(cls, xml_tag: str):
        if xml_tag == "Humans":
            return Species.HUMAN
        if xml_tag == "Werewolves":
            return Species.WEREWOLF
        if xml_tag == "Vampires":
            return Species.VAMPIRE
        raise IncorrectSpeciesException(xml_tag)

    def to_color(self):
        eq_color = {
            Species.HUMAN: "white",
            Species.VAMPIRE: "red",
            Species.WEREWOLF: "blue",
            Species.NONE: "gray",
        }
        return eq_color[self]

    def get_opposite_species(self):
        if self is Species.WEREWOLF:
            return Species.VAMPIRE
        if self is Species.VAMPIRE:
            return Species.WEREWOLF
        raise IncorrectSpeciesException(self)


class Singleton(type):
    """Metaclass that authorize only one instance of a class."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
