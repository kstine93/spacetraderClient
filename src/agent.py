"""
Data and functions related for interacting with the 'agent' endpoint of the Spacetrader API
"""
#==========
from typing import Callable
from .base import SpaceTraderConnection
from .utilities.cache_utilities import dict_cache_wrapper

#==========
class Agent:
    """
    Class to query and edit game data related to the 'Agent' (player information)
    """
    #----------
    stc = SpaceTraderConnection()
    cache_path: str | None = None
    cache_file_name: str | None = None

    #----------
    def __init__(self):
        self.cache_path = self.stc.base_cache_path + "agents/"
        #Using callsign as convenient name for files related to current user:
        self.cache_file_name = "agents"

    #----------
    def cache_agent(func: Callable) -> Callable:
        """
        Wrapper for an external, generic caching system.
        Passes a file path created from system variables and the 'agent' argument of the
        target function as values to the caching system to use in caching the data.
        Target function and its needed arguments (self,agent) also passed on.
        """
        def wrapper(self,callsign:str):
            path = self.cache_path + self.cache_file_name + ".json"
            return dict_cache_wrapper(file_path=path,key=callsign)(func)(self,callsign)
        return wrapper

    #----------
    @cache_agent
    def get_agent(self,callsign:str) -> dict:
        """Get basic information about agent: callsign, account ID, faction, HQ, etc."""
        url = self.stc.base_url + "/my/agent"
        response = self.stc.stc_http_request(method="GET",url=url)
        if not self.stc.response_ok(response): raise Exception(response)
        return {callsign:response['http_data']['data']}
