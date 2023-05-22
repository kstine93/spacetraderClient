#==========
from typing import Callable
from .base import SpaceTraderConnection,DictCacheManager

#==========
class Agent(SpaceTraderConnection,DictCacheManager):
    """
    Class to query and edit game data related to the 'Agent' (player information)
    """
    #----------
    cache_path: str | None = None 
    cache_file_name: str | None = None

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)
        DictCacheManager.__init__(self)
        self.cache_path = self.base_cache_path + "agents/"
        #Using callsign as convenient name for files related to current user:
        self.cache_file_name = "agents"

    #----------
    def cache_agent(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached agent data and if none is found, it calls the given function
        (typically an API call) which provides data. This data is then cached for later use and returned.
        """
        def wrapper(self,**kwargs):
            path = self.cache_path + self.cache_file_name + ".json"
            return DictCacheManager.update_cache_dict_UPDATE(self,path,func,new_key=self.callsign)
        return wrapper

    #----------
    @cache_agent
    def get_agent_details(self,callsign:str) -> dict:
        url = self.base_url + "/my/agent"
        data = self.stc_http_request(method="GET",url=url)
        return {callsign:data['data']}