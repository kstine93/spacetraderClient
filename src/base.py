"""
This file contains the base data + classes used as a foundation for most of the rest of the game.
This file also contains a class for registering a new agent and thereby setting up a new game.
"""

#==========
from urllib3 import PoolManager, HTTPResponse
from .utilities.basic_utilities import *
from .utilities.crypt_utilities import *
from configparser import ConfigParser
import json
from typing import Callable
from warnings import warn
from os import fsdecode,listdir
from time import sleep


#==========
class GameConfig:
    """Very basic class for recording values used by child classes - mostly for filepaths and URLs"""
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
    def count_keys_in_dir(self,dir_path) -> int:
        '''Counts keys across all (JSON) files in a directory'''
        count = 0
        for file in listdir(dir_path):
            file_path = f"{dir_path}/{fsdecode(file)}"
            count += self.count_keys_in_file(file_path)
        return count

    #----------
    def count_keys_in_file(self,file_path) -> int:
        '''Counts keys in JSON file'''
        return sum(1 for key in self.get_keys_in_file(file_path))

    #----------
    def get_keys_in_file(self,file_path) -> int:
        '''Returns keys in JSON file'''
        with open(file_path,"r") as file:
            for key in json.loads(file.read()).keys():
                yield key

    #----------
    def get_dict_from_file(self,file_path:str) -> dict:
        '''Reads and returns dict from file'''
        with open (file_path, "r") as file:
            return json.loads(file.read())

    #---------- 
    def write_dict_to_file(self,file_path:str,data:dict) -> None:
        '''Writes provided dict to file'''
        with open(file_path, "w") as file:
            file.write(json.dumps(data,indent=3))        

    #----------
    def get_cache_dict(self,file_path:str,func:Callable,new_key:str,**kwargs) -> dict:
        '''
        This function is intended to be used as the core of a decorator function.
        This function is for getting a single record that MIGHT be part of a bigger dict in the local cache.
        The function first looks for the record in the dict (is given key present?). If that fails because
        the cache file doesn't exist or the key is not present in the dict,
        we call the given function (typically an API call) to find the data elsewhere.
        We then pass the new data on to 'update_cache_dict' to update the cache.
        '''
        try:
            #Try to open local cache and return record. If this fails, pull from API:
            existing_data = self.get_dict_from_file(file_path)
            return existing_data[new_key]
        except (KeyError, FileNotFoundError):
            data = func(self,new_key)
            self.update_cache_dict(data,file_path)
            return data[new_key]

    #----------
    def update_cache_dict(self,data:dict,file_path:str) -> dict:
        '''
        This function updates a local cache file with a given dictionary. If the file exists,
        we load the file data, update it with the given dictionary, and re-write it. If the file
        doesn't exist, we make a new file with the dictionary as the sole entry.
        '''
        try:
            #Try to get file (but not sure it exists):
            existing_data = self.get_dict_from_file(file_path)
        except FileNotFoundError:
            #If getting file failed, we replace file:
            existing_data = {}
            warn(f"no existing file at {file_path}. New file will be created.")
        finally:
            existing_data.update(data)
            self.write_dict_to_file(file_path,existing_data)


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
        except:
            raise Exception(f"Error in loading API key. Please check API key is present at file path {self.account_config_filepath}")

    #----------
    def load_account_config(self) -> None:
        config = ConfigParser()
        config.read(self.account_config_filepath)
        self.callsign = config['ACCOUNT_CREDENTIALS']['callsign']
        self.encrypted_key = config['ACCOUNT_CREDENTIALS']['key_encrypted']

    #----------
    def load_api_key(self) -> None:
        '''Purpose: Decrypt API key and store it locally so that we can use it for future API calls'''
        password = prompt_user_password("Please enter password to decrypt your API key:")
        decrypted_key_bytes = password_decrypt(self.encrypted_key, password)
        self.api_key = decrypted_key_bytes.decode() #converting to string

    #----------
    def stc_http_response_checker(self, http_response:HTTPResponse) -> bool:
        """Checks general success of the SpaceTrader API call and raises errors/warnings if a failure was found."""  
        #NOTE: Expand this as needed if we want custom handling of certain errors across all SpaceTrader endpoints.
        if http_response.status == 200:
            return True
        else:
            msg = f"API call returned non-200 response. Response data: {http_response.data.decode('utf-8')}"
            raise Exception(msg)

    #----------
    def stc_http_request(self, method:str, url:str, **kwargs) -> dict:
        """Wrapper for HTTP get - implements spacetrader-specific handling of response"""
        http_response = self.http_request(method=method
                                          ,url=url
                                          ,headers=self.default_header
                                          ,**kwargs)
        #If response is o.k., return
        if self.stc_http_response_checker(http_response):
            return json.loads(http_response.data)

    #----------
    def stc_get_paginated_data(self,method:str,url:str,page:str=1,**kwargs) -> None:
        '''
        Generator function for getting paginated data from the SpaceTrader API.
        '''
        limit = 20
        url = f"{url}?limit={limit}"
        while True:
            try:
                new_url = url + f"&page={page}"
                data = self.stc_http_request(method=method,url=new_url,**kwargs)
                data_list = data['data']

                if len(data_list) == 0:
                    break
                yield(data_list)
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
    This class registers a new agent. This class is a bit of an exception to the others used in the game
    in that the methods in this class must be run first before any other game data (e.g., API key) is initialized.
    For that reason, this class holds some repeated values and doesn't rely on the more complex classes.
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
        Receives dictionary response from registering a new agent. Saves account ID, callsign, and encrypted
        API key in a local file. This local file is the basis for which player is playing the game.
        """

        password = prompt_user_password("Please enter a password with which to encrypt the API key")
        bytes_token = dict_to_bytes(new_agent_response['data']['token'])

        encrypted_key_bytes = password_encrypt(bytes_token,password)

        config = ConfigParser()

        credentials = config['ACCOUNT_CREDENTIALS'] = {
            'account_id':new_agent_response['data']['agent']['accountId']
            ,'callsign':new_agent_response['data']['agent']['symbol']
            ,'key_encrypted':encrypted_key_bytes.decode()
        }

        #(Over)writing credentials to local file:
        with open(self.account_config_filepath, 'w') as configfile:
            config.write(configfile)

