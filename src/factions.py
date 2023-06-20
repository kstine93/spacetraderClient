"""
Data and functions related for interacting with the 'factions' endpoint of the Spacetrader API
"""
#==========
from typing import Callable
from .base import SpaceTraderConnection
from .utilities.basic_utilities import get_dict_from_file
from .utilities.cache_utilities import dict_cache_wrapper,update_cache_dict

#==========
class Factions():
    """
    Class to query game data related to the in-game factions
    """
    #----------
    stc = SpaceTraderConnection()
    cache_path: str
    cache_file_name: str

    #----------
    def __init__(self):
        self.base_url = self.stc.base_url + "/factions"
        self.cache_path = self.stc.base_cache_path + "factions/factions.json"
        self.cache_file_name = "factions"

    #----------
    def cache_factions(func: Callable) -> Callable:
        """
        Wrapper for an external, generic caching system.
        Passes a file path created from system variables and the 'faction' argument of the
        target function as values to the caching system to use in caching the data.
        Target function and its needed arguments (self,faction) also passed on.
        """
        def wrapper(self,faction:str):
            path = self.cache_path
            #Reminder: (func) and (self,faction) are being passed as args to nested functions:
            return dict_cache_wrapper(file_path=path,key=faction)(func)(self,faction)
        return wrapper

    #----------
    def reload_factions_in_cache(self,page:int=1) -> None:
        """Updates factions data in cache with data from the API"""
        for faction_list in self.stc.stc_get_paginated_data("GET",self.base_url,page):
            for faction in faction_list["http_data"]["data"]:
                transformed_faction = {faction['symbol']:faction}
                update_cache_dict(transformed_faction,self.cache_path)

    #----------
    def list_all_factions(self) -> dict:
        """Get all contracts associated with the agent"""
        try:
            return get_dict_from_file(self.cache_path)
        except FileNotFoundError:
            self.reload_factions_in_cache()
            return get_dict_from_file(self.cache_path)

    #----------
    @cache_factions
    def get_faction(self,faction:str) -> dict:
        """Get information about a specific faction"""
        url = self.base_url + "/" + faction
        response = self.stc.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with factions dict:
        return  {faction:response['http_data']['data']}
