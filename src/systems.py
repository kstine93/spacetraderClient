"""
Data and functions related for interacting with the 'systems' endpoint of the Spacetrader API
"""
#==========
from typing import Callable
from .base import SpaceTraderConnection
from .utilities.custom_types import SpaceTraderResp
from .utilities.basic_utilities import count_keys_in_dir
from .utilities.cache_utilities import dict_cache_wrapper,update_cache_dict

#==========
class Systems:
    """
    Class to query and edit game data related to systems.
    """
    #----------
    stc = SpaceTraderConnection()
    base_url: str
    cache_path: str

    #----------
    def __init__(self):
        self.base_url = self.stc.base_url + "/systems"
        self.cache_path = self.stc.base_cache_path + "systems/"

    #----------
    def simplify_system_dict(self,system_dict:dict) -> dict:
        """Removing arguably unneeded waypoints info from the 'system' dictionary.
        Particularly relevant once enriched from scanning waypoints."""
        keys_to_remove = ['x','y','orbitals','systemSymbol','chart']
        waypoints = system_dict['waypoints']
        for wp in waypoints:
            for key in keys_to_remove:
                wp.pop(key,None)
            #reducing traits to a simple string list:
            if 'traits' in wp.keys():
                wp['traits'] = [tr['symbol'] for tr in wp['traits']]
        system_dict['waypoints'] = waypoints
        return system_dict

    #----------
    def __mold_system_dict(self,response:SpaceTraderResp) -> dict:
        """Transform systems data into an easier-to-use format for inserting into dictionaries"""
        if not self.stc.response_ok(response): raise Exception(response)
        data = response['http_data']['data']
        return {data['symbol']:data}

    #----------
    def __create_cache_path(self,system:str) -> str:
        """Create cache path from system string. To shard data, we're using the first 4
        characters of the system string as the file path (only last character varies A-Z)"""
        return self.cache_path + system[0:4] + ".json"

    #----------
    def cache_system(func: Callable) -> Callable:
        """
        Wrapper for an external, generic caching system.
        Passes a file path created from system variables and the 'system' argument of the
        target function as values to the caching system to use in caching the data.
        Target function and its needed arguments (self,system) also passed on.
        """
        def wrapper(self,system:str):
            path = self.__create_cache_path(system)
            #Reminder: (func) and (self,system) are being passed as args to nested functions:
            return dict_cache_wrapper(file_path=path,key=system)(func)(self,system)
        return wrapper

    #----------
    def reload_systems_in_cache(self,page:int=1) -> None:
        """Force-updates all systems data in cache with data from the API"""
        for system_list in self.stc.stc_get_paginated_data("GET",self.base_url,page):
            for sys in system_list['http_data']['data']:
                transformed_sys = {sys['symbol']:sys}
                #Using first 4 characters of the system symbol as file name:
                file_path = self.__create_cache_path(sys['symbol'])
                update_cache_dict(transformed_sys,file_path)

    #----------
    def count_systems_in_cache(self) -> int:
        return count_keys_in_dir(self.cache_path)

    #----------
    @cache_system
    def get_system(self,system:str) -> dict:
        """Returns basic overview of a given system. Decorator pulls from cached data if exists"""
        url = self.base_url + "/" + system
        response = self.stc.stc_http_request(method="GET",url=url)
        data = self.__mold_system_dict(response)
        return data

    #----------
    def get_shipyard(self,waypoint:str) -> dict:
        """Returns information about what ships are available at a given shipyard waypoint"""
        system = self.stc.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/shipyard"
        response = self.stc.stc_http_request(method="GET",url=url)
        if not self.stc.response_ok(response): return {}
        return response['http_data']['data']

    #----------
    def get_jump_gate(self,waypoint:str) -> dict:
        """Returns information about what systems may be jumped to from a given jumpgate waypoint"""
        system = self.stc.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/jump-gate"
        response = self.stc.stc_http_request(method="GET",url=url)
        if not self.stc.response_ok(response): return {}
        return response['http_data']['data']
