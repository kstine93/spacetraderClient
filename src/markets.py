"""
Data and functions related for interacting with the 'systems' endpoint of the Spacetrader API
"""
#==========
from typing import Callable
from .base import SpaceTraderConnection
from .utilities.custom_types import SpaceTraderResp
from .utilities.cache_utilities import dict_cache_wrapper,update_cache_dict

#==========
class Markets:
    """
    Class to query and edit game data related to systems.
    """
    #----------
    stc = SpaceTraderConnection()
    base_url: str | None = None
    cache_path: str | None = None

    #----------
    def __init__(self):
        self.base_url = self.stc.base_url + "/systems"
        self.cache_path = self.stc.base_cache_path + "markets/"

    #----------
    def mold_market_dict(self,response:SpaceTraderResp) -> dict:
        """Transform systems data into an easier-to-use format for inserting into dictionaries"""
        if not self.stc.response_ok(response): raise Exception(response)
        data = response['http_data']['data']
        data = self.simplify_market_dict(data)
        return {data['symbol']:data}

    #----------
    def simplify_market_dict(self,market_dict:dict) -> dict:
        """Transform market data into an easier-to-use format with less extra data"""
        market_dict.pop("transactions",None) #Removing info on past transactions
        for key in ['imports','exports','exchange']:
            market_dict[key] = [item['symbol'] for item in market_dict[key]]
        return market_dict

    #----------
    def create_cache_path(self,system:str) -> str:
        """Create cache path from system string. To shard data, we're using the first 4
        characters of the system string as the file path (only last character varies A-Z)"""
        return self.cache_path + system[0:4] + ".json"

    #----------
    def cache_market(func: Callable) -> Callable:
        """
        Wrapper for an external, generic caching system.
        Passes a file path created from system variables and the 'waypoint' argument of the
        target function as values to the caching system to use in caching the data.
        Target function and its needed arguments (self,waypoint) also passed on.
        """
        def wrapper(self,waypoint:str):
            system = self.stc.get_system_from_waypoint(waypoint)
            path = self.create_cache_path(system)
            return dict_cache_wrapper(file_path=path,key=waypoint)(func)(self,waypoint)
        return wrapper

    #----------
    @cache_market
    def get_market(self,waypoint:str) -> dict:
        """Returns information about what commodities may be bought/sold at a market waypoint"""
        system = self.stc.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/market"
        response = self.stc.stc_http_request(method="GET",url=url)
        data = self.mold_market_dict(response)
        return data

    #----------
    def update_market(self,waypoint:str) -> dict:
        """gets market data and force-updates market cache"""
        system = self.stc.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/market"
        response = self.stc.stc_http_request(method="GET",url=url)
        data = self.mold_market_dict(response)
        file_path = self.create_cache_path(system)
        update_cache_dict(data,file_path)
        return data[waypoint]
