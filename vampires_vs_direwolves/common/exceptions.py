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


class GameProtocolException(BaseGameException):
    """Command conventions not respected"""
    pass
