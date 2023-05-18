#==========
from typing import Callable
from .base import SpaceTraderConnection,CacheManager

#==========
class Factions(SpaceTraderConnection,CacheManager):
    """
    Class to query game data related to the in-game factions
    """
    #----------
    cache_path: str | None = None 
    cache_file_name: str | None = None

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)
        CacheManager.__init__(self)
        self.cache_path = self.base_cache_path + "factions/"
        #WARNING: I am using a static name "factions" below because I don't think factions change by game
        #(so I can use factions across all of my games). I can reverse this by using `self.callsign` instead.
        self.cache_file_name = "factions"

    #----------
    def cache_faction(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached faction data and tries to find information about the given faction.
        If no cache file exists, one is created.
        """
        def wrapper(self,**kwargs):
            new_path = self.cache_path + self.cache_file_name + ".json"
            return CacheManager.read_dict_cache(self,new_path,func,**kwargs)
        return wrapper
    
    #----------
    def update_faction(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached faction data and tries to find information about the given faction.
        If no cache file exists, one is created. If the file exists, but there is no data on the given faction,
        This information is added to the file.
        """
        def wrapper(self,faction,**kwargs):
            new_path = self.cache_path + self.cache_file_name + ".json"
            # kwargs.update({"key":faction})
            return CacheManager.update_dict_cache(self,new_path,faction,func,**kwargs)
        return wrapper

    #----------
    @cache_faction
    def list_factions(self) -> dict:
        url = self.base_url + "/factions"
        data = self.stc_http_request(method="GET",url=url)
        #Transforming nested list to dict to make data easier to reference:
        return {obj['symbol']:obj for obj in data['data']}
    
    #----------
    @update_faction
    def get_faction(self,faction:str) -> dict:
        url = self.base_url + "/factions/" + faction
        new_data = self.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with factions dict:
        return {faction:new_data['data']}