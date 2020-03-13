# -*- coding: utf-8 -*-
from boutchou.abstract_ai import AbstractAI, AbstractSafeAI
from boutchou.boutchou_ai import Boutchou
from boutchou.random_ai import RandomAI
from boutchou.default_ai import DefaultAI
from boutchou.human_ai import HumanAI
from boutchou.rush_to_opponent_ai import RushToOpponentAI, MoveToHumanOrMoveToOpponentIfBetter
from boutchou.rush_to_humans_ai import RushToHumansAI, MoveToBestHumans
from boutchou.multi_split_ai import MultiSplitAI
from boutchou.tkinter_ai import TkinterHumanAI

__all__ = [
    'AbstractAI',
    'AbstractSafeAI',
    'Boutchou',
    'RandomAI',
    'DefaultAI',
    'RushToHumansAI',
    'MoveToHumanOrMoveToOpponentIfBetter',
    'MoveToBestHumans',
    'RushToOpponentAI',
    'MultiSplitAI',
    'HumanAI',
    'TkinterHumanAI',
]
