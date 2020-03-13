# -*- coding: utf-8 -*-
from boutchou.abstract_ai import AbstractAI, AbstractSafeAI
from boutchou.alpha_beta_ai import AlphaBetaAI
from boutchou.boutchou_ai import Boutchou
from boutchou.default_ai import DefaultAI
from boutchou.multi_split_ai import MultiSplitAI
from boutchou.random_ai import RandomAI
from boutchou.rush_to_humans_ai import MoveToBestHumans, RushToHumansAI
from boutchou.rush_to_opponent_ai import RushToOpponentAI
from boutchou.tkinter_ai import TkinterHumanAI

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

    'TkinterHumanAI',
]
