# -*- coding: utf-8 -*-
class BaseGameException(Exception):
    """Base exception class"""
    pass


class MapCorruptedException(BaseGameException):
    """Map contains invalid data, such 2 different species."""
    pass


class SpeciesExtinctionException(BaseGameException):
    """No more movement possible because species is extinct"""
    pass


class IncorrectSpeciesException(BaseGameException):
    """Invalid species for the current action"""
    pass


class GameProtocolException(BaseGameException):
    """Command conventions not respected"""
    pass


class IncorrectCommandException(BaseGameException):
    """Invalid command name"""
    pass


class TooMuchConnections(Exception):
    pass


class PlayerCheatedException(Exception):
    pass


class PlayerTimeoutError(Exception):
    pass
