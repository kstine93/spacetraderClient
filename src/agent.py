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
        This version reads the cached agent data and tries to find information about a given agent.
        If the file exists, but there is no data on the given agent, this information is added to the file.
        If no file exists, a file is created and the data added to it.
        """
        def wrapper(self,callsign:str,**kwargs):
            path = self.cache_path + self.cache_file_name + ".json"
            return DictCacheManager.get_cache_dict(self,path,func,new_key=callsign,**kwargs)
        return wrapper

    #----------
    @cache_agent
    def get_agent(self,callsign:str) -> dict:
        url = self.base_url + "/my/agent"
        data = self.stc_http_request(method="GET",url=url)
        return {callsign:data['http_data']['data']}