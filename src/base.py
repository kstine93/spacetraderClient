"""
This file contains the base data + classes used as a foundation for most of the rest of the game.
This file also contains a class for registering a new agent and thereby setting up a new game.
"""

#==========
from urllib3 import PoolManager, HTTPResponse
from .utilities.basic_utilities import *
from .utilities.crypt_utilities import *
from .utilities.custom_types import SpaceTraderResp
from configparser import ConfigParser
import json
from typing import Callable
from time import sleep


#==========
class GameConfig:
    """Very basic class for recording values used by child classes
    mostly for filepaths and URLs"""
    #----------
    account_config_filepath:str = "./account_info.cfg"
    base_cache_path:str = "./gameData/"
    base_url:str = "https://api.spacetraders.io/v2"

    #----------
    def __init__(self):
        pass


#==========
class DictCacheManager(GameConfig):
    """Generic class for loading data to/from a cache or local file system"""

    #----------
    def __init__(self):
        pass

    #----------
    def get_cache_dict(self,file_path:str,func:Callable,new_key:str,**kwargs) -> dict:
        """
        This function is intended to be used as the core of a decorator function.
        This function is for getting a single record that MIGHT be part of a bigger dict in
        the local cache. The function first looks for the record in the dict (is given key present?)
        If that fails becausethe cache file doesn't exist or the key is not present in the dict,
        we call the given function (typically an API call) to find the data elsewhere.
        We then pass the new data on to 'update_cache_dict' to update the cache.
        """
        existing_data = attempt_dict_retrieval(file_path)
        if new_key in existing_data.keys():
            return existing_data[new_key]
        else:
            data = func(self,new_key)
            self.update_cache_dict(data,file_path)
            return data[new_key]

    #----------
    def update_cache_dict(self,data:dict,file_path:str) -> dict:
        """
        This function updates a local cache file with a given dictionary. If the file exists,
        we load the file data, update it with the given dictionary, and re-write it. If the file
        doesn't exist, we make a new file with the dictionary as the sole entry.
        """
        existing_data = attempt_dict_retrieval(file_path)
        existing_data.update(data)
        write_dict_to_file(file_path,existing_data)

#==========
class HttpConnection:
    """Generic class for making API requests"""
    #----------
    conn:PoolManager | None = None

    #----------
    def __init__(self):
        self.conn = PoolManager()

    #----------
    def http_request(self, method:str, url:str, **kwargs) -> HTTPResponse:

        if 'body' in kwargs:
            kwargs.update({'body':json.dumps(kwargs['body'])})

        return self.conn.request(
            method=method
            ,url=url
            ,**kwargs
        )

#==========
class SpaceTraderConnection(HttpConnection,GameConfig):
    """
    Class that enables API usage for the SpaceTrader game
    - primarily by loading and storing api and base url of endpoint
    """
    #----------
    callsign:str | None = None
    encrypted_key: str | None = None

    api_key: str | None = None
    default_header: dict = {"Accept": "application/json"}

    #----------
    def __init__(self):
        HttpConnection.__init__(self)

        #Loading in config which has basic information on player:
        self.load_account_config()
        try:
            self.load_api_key()
            self.default_header.update({"Authorization" : "Bearer " + self.api_key})
        except Exception as e:
            msg = f"Error in loading API key.\
                Please check API key is present at file path {self.account_config_filepath}"
            raise e(msg)

    #----------
    def load_account_config(self) -> None:
        """Account info is stored in a local file for persistence.
        Loading these in (particularly encrypted key)
        is necessary to start using this game client."""
        config = ConfigParser()
        config.read(self.account_config_filepath)
        self.callsign = config['ACCOUNT_CREDENTIALS']['callsign']
        self.encrypted_key = config['ACCOUNT_CREDENTIALS']['key_encrypted']

    #----------
    def load_api_key(self) -> None:
        """Purpose: Decrypt API key and store it locally so that we can use it
        for future API calls"""
        password = get_user_password(prompt="Please enter password to decrypt your API key:"
                                     ,password_name="SPACETRADER_PASSWORD")
        decrypted_key_bytes = password_decrypt(self.encrypted_key, password)
        self.api_key = decrypted_key_bytes.decode() #converting to string

    #----------
    def repackage_http_response(self,http_response:HTTPResponse) -> SpaceTraderResp:
        """Transforms http_response (sometimes in a complex format) to simple dictionary."""
        packet = {
            'http_data':json.loads(http_response.data),
            'http_status':http_response.status
        }
        return packet

    #----------
    def get_system_from_waypoint(self,waypoint:str) -> str:
        """In Alpha version of the game, the system is the first 7 characters of the waypoint.
        Rather than pass both values around, this derives system from waypoint"""
        return waypoint[0:7]

    #----------
    def stc_http_request(self, method:str, url:str, **kwargs) -> dict:
        """Wrapper for HTTP get - implements spacetrader-specific handling of response"""
        http_response = self.http_request(method=method
                                          ,url=url
                                          ,headers=self.default_header
                                          ,**kwargs)

        return self.repackage_http_response(http_response)

    #----------
    def stc_get_paginated_data(self,method:str,url:str,page:str=1,**kwargs) -> None:
        """Generator function for getting paginated data from the SpaceTrader API."""
        #NOTE: The speed of this is heavily constrained by API limits (<2 per second).
        # If the API limits are raised, we could remove the sleep function and try
        # to parallelize this more.
        limit = 20
        url = f"{url}?limit={limit}"
        while True:
            try:
                new_url = url + f"&page={page}"
                response = self.stc_http_request(method=method,url=new_url,**kwargs)
                if len(response['http_data']['data']) == 0:
                    break
                yield(response)
                page += 1
                #Sleeping to avoid over-drawing from API.
                sleep(0.05)
            except Exception as e:
                #If system fails mid-cache, return page (shows progress for re-trying):
                print(page)
                raise e

#==========
class RegisterNewAgent(HttpConnection,GameConfig):
    """
    This class registers a new agent. This class is a bit of an exception to the others used
    in the game in that the methods in this class must be run first before any other game data
    (e.g., API key) is initialized. For that reason, this class holds some repeated values and
    doesn't rely on the more complex classes.
    """

    #----------
    def __init__(self):
        HttpConnection.__init__(self)
        GameConfig.__init__(self)

    #----------
    def register_new_agent(self, agent_callsign:str, faction:str = "COSMIC") -> dict:
        """
        Register a new player with the game.
        Returns dictionary with agent metadata (as well as other ship + contract information)
        """
        body = {
            'symbol':agent_callsign
            ,'faction':faction
        }
        headers={'Content-Type': 'application/json'}
        url = self.base_url + "/register"

        http_response = self.http_request("POST",url=url,body=body,headers=headers)
        data = bytes_to_dict(http_response.data)
        self.save_agent_metadata_locally(data)

    #----------
    def save_agent_metadata_locally(self, new_agent_response:dict) -> None:
        """
        Receives dictionary response from registering a new agent. Saves account ID, callsign,
        and encrypted API key in a local file. This local file is the basis for which player
        is playing the game.
        """

        password = get_user_password(prompt="Please enter password to decrypt your API key:"
                                     ,password_name="SPACETRADER_PASSWORD")
        bytes_token = dict_to_bytes(new_agent_response['data']['token'])

        encrypted_key_bytes = password_encrypt(bytes_token,password)

        config = ConfigParser()

        config['ACCOUNT_CREDENTIALS'] = {
            'account_id':new_agent_response['data']['agent']['accountId']
            ,'callsign':new_agent_response['data']['agent']['symbol']
            ,'key_encrypted':encrypted_key_bytes.decode()
        }

        #(Over)writing credentials to local file:
        with open(self.account_config_filepath, 'w') as configfile:
            config.write(configfile)

