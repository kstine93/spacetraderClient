#==========
from typing import Callable
from .base import SpaceTraderConnection,DictCacheManager

#==========
class Factions(SpaceTraderConnection,DictCacheManager):
    """
    Class to query game data related to the in-game factions
    """
    #----------
    cache_path: str | None = None
    cache_file_name: str | None = None

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)
        DictCacheManager.__init__(self)
        self.base_url = self.base_url + "/factions"
        self.cache_path = self.base_cache_path + "factions/"
        self.cache_file_name = "factions"

    #----------
    def cache_factions(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached faction data and tries to find information about
        the given faction. If the file exists, but there is no data on the given faction, this
        information is added to the file.
        If no file exists, a file is created and the data added to it.
        """
        def wrapper(self,faction:str,**kwargs):
            path = self.cache_path + self.cache_file_name + ".json"
            return DictCacheManager.get_cache_dict(self,path,func,new_key=faction,**kwargs)
        return wrapper

    #----------
    def reload_factions_into_cache(self,page:int=1) -> None:
        """Updates factions data in cache with data from the API"""
        path = self.cache_path + self.cache_file_name + ".json"
        for faction_list in self.stc_get_paginated_data("GET",self.base_url,page):
            for faction in faction_list:
                transformed_faction = {faction['symbol']:faction}
                self.update_cache_dict(transformed_faction,path)

    #----------
    @cache_factions
    def get_faction(self,faction:str) -> dict:
        """Get information about a specific faction"""
        url = self.base_url + "/" + faction
        response = self.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with factions dict:
        return  {faction:response['http_data']['data']}
