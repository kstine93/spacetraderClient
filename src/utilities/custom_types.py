"""
This file contains custom types or enumerations for the spacetrader game:
"""

#==========
from typing import TypedDict
from enum import Enum

#==========
class SpaceTraderResp(TypedDict):
    '''Responses from the SpaceTrader API are transformed into this standard dictionary upon retrieval
    before further processing'''
    http_data:str
    http_status:int


#==========
class RefinableProduct(Enum):
    '''Product that can be refined using 'Ship Refine' endpoint within Ships class'''
    IRON = 1
    COPPER = 2
    SILVER = 3
    GOLD = 4
    ALUMINUM = 5
    PLATINUM = 6
    URANITE = 7
    MERITIUM = 8
    FUEL = 9

#==========
class NavSpeed(Enum):
    '''Navigation speed can be set and only allows a few values'''
    DRIFT = 1
    STEALTH = 2
    CRUISE = 3
    BURN = 4
