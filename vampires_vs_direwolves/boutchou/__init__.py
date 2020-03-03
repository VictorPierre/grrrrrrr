# -*- coding: utf-8 -*-
from boutchou.abstract_ai import AbstractAI, AbstractSafeAI
from boutchou.boutchou_ai import Boutchou
from boutchou.random_ai import RandomAI
from boutchou.default_ai import DefaultAI
from boutchou.rush_to_humans_ai import RushToHumansAI, MoveToBestHumans
from boutchou.rush_to_opponent_ai import RushToOpponentAI
from boutchou.multi_split_ai import MultiSplitAI

__all__ = [
    'AbstractAI',
    'AbstractSafeAI',
    'Boutchou',
    'RandomAI',
    'DefaultAI',
    'RushToHumansAI',
    'MoveToBestHumans',
    'RushToOpponentAI',
    'MultiSplitAI',
]
