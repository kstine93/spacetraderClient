#==========
from typing import Callable
from .base import SpaceTraderConnection,DictCacheManager
from time import sleep
from os import listdir, fsdecode
import json
from datetime import datetime

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
    def update_systems(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached systems data and tries to find information about the given system.
        If the file exists, but there is no data on the given system, this information is added to the file.
        If no file exists, a warning is given but NO FILE IS CREATED.
        """
        def wrapper(self,system_symbol:str,**kwargs):
            new_path = self.cache_path + self.cache_file_name + ".json"
            return DictCacheManager.update_cache_dict(self,new_path,system_symbol,func,**kwargs)
        return wrapper

    #----------
    def refresh_all_systems() -> None:
        #optional function I could implement later- upon initialization of this class, if the 'systems' files are
        #older than a certain limit (e.g., created date > 30 days in past) then I would refresh the files by reloading them.
        #BUT: this assumes systems data will actually change and therefore need refreshing.
        pass         

    #----------
    def cache_all_systems(self,page:str=1) -> None:
        for system_list in self.stc_get_paginated_data("GET",self.base_url,page):
            for sys in system_list:
                transformed_sys = {sys['symbol']:sys}
                #Using first 4 characters of the system symbol as file name:
                file_path = self.cache_path + sys['symbol'][0:4] + ".json"
                self.force_update_cache_dict(file_path,transformed_sys)
                #update_cache_dict(self,file_path:str,new_key:str,func:Callable,force:bool,**kwargs)
                #update_cache_dict

    #----------
    def test():
        """
        I need to iterate with the generator.
        for each page of results, I need to split the results and cache each value.
        """
        pass

    #----------
    def count_systems_in_cache(self) -> int:
        return self.count_keys_in_dir(self.cache_path)

    #----------
    def get_system(self,system:str) -> dict:
        url = self.base_url + "/" + system
        new_data = self.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with systems dict:
        return {new_data['data']['symbol']:new_data['data']}