#==========
from typing import Callable
from .base import SpaceTraderConnection,DictCacheManager

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
    def refresh_all_systems() -> None:
        #optional function I could implement later- upon initialization of this class, if the 'systems' files are
        #older than a certain limit (e.g., created date > 30 days in past) then I would refresh the files by reloading them.
        #BUT: this assumes systems data will actually change and therefore need refreshing.
        pass         

    #----------
    def reload_systems_into_cache(self,page:str=1) -> None:
        #NOTE: The speed of this is heavily constrained by API limits (<2 per second). This function (with a 100ms sleep)
        #does 1.3 records per second. If the API limits are raised, we could try to parallelize this more.
        for system_list in self.stc_get_paginated_data("GET",self.base_url,page):
            for sys in system_list:
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
        url = self.base_url + "/" + system
        new_data = self.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with systems dict:
        return {new_data['data']['symbol']:new_data['data']}