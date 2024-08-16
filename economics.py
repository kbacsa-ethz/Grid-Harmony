# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 14:46:43 2024

@author: schakraborth
"""

from constants import *

class EnergySource:
    def __init__(self, type, fixed_cost, operational_cost):
        self.type = type
        self.fixed_cost = fixed_cost
        self.operational_cost = operational_cost