#==========
from typing import Callable
from .base import SpaceTraderConnection,DictCacheManager
from .custom_types import SpaceTraderResp

#==========
class Systems(SpaceTraderConnection,DictCacheManager):
    """
    Class to query and edit game data related to systems.
    """
    #----------
    cache_path: str | None = None 
    cache_file_name: str | None = None

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)
        DictCacheManager.__init__(self)
        self.base_url = self.base_url + "/systems"
        self.cache_path = self.base_cache_path + "systems/"
        self.cache_file_name = "systems"

    #----------
    def mold_system_dict(self,response:SpaceTraderResp) -> dict:
        data = response['http_data']['data']
        {data['symbol']:data}

    #----------
    def cache_system(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached systems data and tries to find information about the given system.
        If the file exists, but there is no data on the given system, this information is added to the file.
        If no file exists, a file is created and the data added to it.
        """
        def wrapper(self,system:str,**kwargs):
            path = self.cache_path + system[0:4] + ".json"
            return DictCacheManager.get_cache_dict(self,path,func,new_key=system,**kwargs)
        return wrapper      

    #----------
    def reload_systems_into_cache(self,page:str=1) -> None:
        """Updates contracts data in cache with data from the API"""
        for system_list in self.stc_get_paginated_data("GET",self.base_url,page):
            for sys in system_list['http_data']['data']:
                transformed_sys = {sys['symbol']:sys}
                #Using first 4 characters of the system symbol as file name:
                file_path = self.cache_path + sys['symbol'][0:4] + ".json"
                self.update_cache_dict(transformed_sys,file_path)

    #----------
    def count_systems_in_cache(self) -> int:
        return self.count_keys_in_dir(self.cache_path)

    #----------
    @cache_system
    def get_system(self,system:str) -> dict:
        """Returns basic overview of a given system. Decorator pulls from cached data if it exists"""
        url = self.base_url + "/" + system
        response = self.stc_http_request(method="GET",url=url)
        data = self.mold_system_dict(response)
        return data

    #----------
    def get_market(self,waypoint:str) -> dict:
        """Returns information about what commodities may be bought or sold at a given market waypoint"""
        system = self.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/market"
        response = self.stc_http_request(method="GET",url=url)
        return response
    
    #----------
    def get_shipyard(self,waypoint:str) -> dict:
        """Returns information about what ships are available at a given shipyard waypoint"""
        system = self.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/shipyard"
        response = self.stc_http_request(method="GET",url=url)
        return response

    #----------
    def get_jump_gate(self,waypoint:str) -> dict:
        """Returns information about what systems may be jumped to from a given jumpgate waypoint"""
        system = self.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/jump-gate"
        response = self.stc_http_request(method="GET",url=url)
        return response
