#----------
# Goals of this file:
# 1. List initial commands for starting Spacetraders game
#----------

import configparser
from .utilities.basic_utilities import *
from typing import Callable

from .base import SpaceTraderConnection,SpaceTraderCacheManager


#==========
class Agent(SpaceTraderConnection,SpaceTraderCacheManager):
    """
    This class is to do everything related to the agent, including:
    1. Initialize the agent (for new players)
    2. Query current agent metadata
    3. Edit current agent metadata

    NOTE: I would also like this class to somehow work with local files - we don't need to always query the API for most data,
    let's cache it locally instead. We're already doing this on a basic level with callsign + account_ID. We can include
    faction data in this, home system info, etc. We can make this just a JSON document with account_ID (or callsign) as the key.
    This will require that this class be flexible though - we will need to look locally for a record - and if we can't find it -
    query it AND store it locally for future use (we can set up some kind of refresh system to automatically flag existing
    records as old and in need of refreshing from the API every X minutes if we want (more relevant for other data in the game
    though)).
    This suggests another base class that can be used alongside the connection class I already have. This other class would have
    basic capabilities to manage the file system - file paths, wrapper functions for reading / writing files, consistent
    formatting standards, etc.

    NEXT STEPS:
    1. Let's manually set up a few files and the code here to write them, then we can transform this logic into a class.
    """
    #----------
    cache_path: str = SpaceTraderCacheManager.base_cache_path + "agents/"
    cache_file_name: str = SpaceTraderCacheManager.base_cache_file_name
    test5 = "agent_value"

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)
        SpaceTraderCacheManager.__init__(self)

        #Transforming API key to serve as unique file name:
        # self.cache_file_name = self.transform_file_name(self.api_key)
        # print("p_"+self.cache_file_name)
        # print("p_"+self.cache_path)

    #----------
    def read_write(self,func:Callable,file_name_path:str,**kwargs):
        try:
            with open(file_name_path, "r") as file:
                return json.loads(file.read())
        except:
            data = func(self, **kwargs)
            with open(file_name_path, "w") as file:
                file.write(json.dumps(data,indent=3))
            return data  

    #----------
    def agent_decorator(func: Callable):
        def wrapper(self,**kwargs):
            new_path = self.cache_path + self.test5 + ".json"
            return SpaceTraderCacheManager.read_dict_cache_v2(self,new_path,func,**kwargs)
        return wrapper

    #----------
    # CURRENT PROBLEM TO SOLVE:
    # I have accomplished the following:
    # - Implemented decorator function in parent class
    # - Modified decorator function to allow for variables
    #
    # However, the issue is now that the variables themselves cannot change in the runtime of the code.
    # The reason for this seems to be that Python is creating new versions of the functions before the code
    # actually runs. So, if those variables don't exist until the class is initialized, THAT WON'T WORK.
    # 
    # WHAT I WANT:
    # I want to be able to use dynamic variables to modify how the decorator function behaves, but it seems like
    # that's not possible. I could handle this a couple of different ways:
    # 1. It's possible to use variables initialized in the parent function - so I could read from a config in CacheManager to
    #   set the values, but this would have the disadvantage that I could ONLY use the one file name (although this could be o.k.
    #   - if I needed to use a function-provided filename, I could do this in another decorator method...)
    #
    #   - UPDATE: I can use class-initialized variables in the inner decorator function - and these DEFAULT TO THE CLASS
    #       IN WHICH THE DECORATOR IS CALLED. This is kind of nice- but could be super confusing. I don't really want to
    #       rely on 'self' in the inner function...
    #   - NEXT STEP: Let's experiment with breaking apart the outer decorator wrapper and putting it elsewhere - or with keeping
    #       this decorator function in an external function somehow.
    #
    # 2. I could embed file name attributes to the underlying function call - but this seems really bad. I don't want to mix values
    #    intended for the decorator into those function calls.
    # 
    # ADDITIONAL TO TEST:
    # 1. How does a decorator-with-parameters work outside of a class if the parameters are not initialized until later in the code?
    #
    # I think I need to go for #1. It's not as flexible as I'd like, but it's the only way I can see of using class variables
    # in decorator parameters.
    # -Kevin, May 15, 2023
    #@SpaceTraderCacheManager.get_dict_cache(path=cache_path,file_name=cache_file_name)
    @agent_decorator
    def get_agent_details(self) -> dict:
        url = self.base_url + "/my/agent"
        return self.stc_http_request(method="GET",url=url)

    #----------
    def register_new_agent(self, agent_callsign:str, faction:str = "COSMIC") -> dict:

        #Register a new player with the game.
        #Returns dictionary with agent metadata (as well as other ship + contract information)

        body = {
            'symbol':agent_callsign
            ,'faction':faction
        }
        headers={'Content-Type': 'application/json'}
        url = self.base_url + "/register"

        http_response = self.http_post(url=url,body=body,headers=headers)

        return bytes_to_dict(http_response.data)

    #----------
    def save_agent_metadata_locally(self, new_agent_response:dict
                                    ,local_cfg_filepath:str = "./account_info.cfg") -> None:
        
        #Receives dictionary response from registering a new agent.
        #Saves account ID, callsign, and encrypted API key in a local file.

        password = prompt_user_password("Please enter a password with which to encrypt the API key")
        bytes_token = dict_to_bytes(new_agent_response['data']['token'])

        encrypted_key_bytes = password_encrypt(bytes_token,password)

        config = configparser.ConfigParser()
        config.read(local_cfg_filepath)

        credentials = config['ACCOUNT_CREDENTIALS'] = {
            'account_id':new_agent_response['data']['agent']['accountId']
            ,'callsign':new_agent_response['data']['agent']['symbol']
            ,'key_encrypted':encrypted_key_bytes.decode() #converting bytes to string with .decode()
        }

        #(Over)writing credentials to local file:
        with open(local_cfg_filepath, 'w') as configfile:
            config.write(configfile)