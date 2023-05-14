#----------
# Goals of this file:
# 1. List initial commands for starting Spacetraders game
#----------

import configparser
from .utilities.basic_utilities import *

from .base import SpaceTraderConnection
import json

#==========
class Agent(SpaceTraderConnection):
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
    cache_path: str = "gameData/agents/"

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)

    #----------
    def attempt_cache_retrieval(func):
        """
        Intended to be used prior to API calls which gather information about the world.
        This decorator function searches for a relevant file in a file path. If it finds it, it skips the
        API call. If it does NOT find the data, it calls the API, fills in the missing data, and then returns the data.
        """

        # TODO: Make this function nicer:
        # 1. Decide where to put this code - in a higher-level class?
        # 2. Look if I need more versions of this (e.g., for appending rather than overwriting files) 
        def wrapper(self, **kwargs):
            path = self.cache_path
            prefix = self.cache_file_prefix

            try:
                with open(path + prefix + ".json", "r") as file:
                    return json.loads(file.read())

            except:
                data = func(self, **kwargs)
                with open(path + self.cache_file_prefix + ".json", "w") as file:
                    file.write(json.dumps(data,indent=3))
                return data
            
        return wrapper    

    #----------
    @attempt_cache_retrieval
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