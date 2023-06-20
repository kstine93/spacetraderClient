"""
This file contains custom types or enumerations for the spacetrader game:
"""

#==========
from typing import TypedDict
from enum import Enum

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

#==========
class SpaceTraderResp(TypedDict):
    '''Responses from the SpaceTrader API are transformed into this standard dictionary upon retrieval
    before further processing'''
    http_data:dict
    http_status:int


#==========
#NOTE: PriceRecord is a little inaccurate in that this definition allows any number of items,
#whereas its use in the codebase usually refers to a dictionary with only 1 item.
'''
priceRecord = {"X1-LJ2DS-RSE": 340}
'''
PriceRecord = dict[str,int]

#==========
'''
priceObj = {
    "purchase_prices": {
        "X1-LJ2DS-RSE": 340,
        "X1-SFL31-F3D": 394
    },
    "sell_prices": {
        "X1-LJ2DS-RSE": 324,
        "X1-SFL31-F3D": 355
    }
}
'''
PriceObj = dict[str,PriceRecord]


#==========
'''
marginObj = {
    "item":"COPPER",
    "sell":{"X1-SFL31-F3D": 355},
    "buy":{"X1-SFL31-F3D": 394},
    "margin": -39
}
'''
class MarginObj(TypedDict):
    item:str
    sell:PriceRecord
    buy:PriceRecord
    margin:int