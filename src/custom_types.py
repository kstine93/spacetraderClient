"""
This file contains custom types or enumerations for the spacetrader game:
"""

#==========
from typing import TypedDict

#==========
class SpaceTraderResp(TypedDict):
    '''Responses from the SpaceTrader API are transformed into this standard dictionary upon retrieval
    before further processing'''
    http_data:str
    http_status:int

    