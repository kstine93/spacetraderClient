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
class CacheManager(GameConfig):
    """Generic class for loading data to/from a cache or local file system"""

    #----------
    def __init__(self):
        pass

    #----------
    def read_dict_cache(self,file_name_path:str,func:Callable,**kwargs) -> dict:
        '''
        This function is intended to be used as the core of a decorator function.
        This function is looking for json data in a specified filepath and returning it if it exists.
        If it fails to retrieve this file, it calls the passed function (which must return a dict object).
        This dict object is then written to the given path and also returned to the caller.
        A common function to pass in would be an API call - which gets executed if no local data is found.
        '''
        try:
            with open(file_name_path, "r") as file:
                return json.loads(file.read())
        except:
            data = func(self,**kwargs)
            with open(file_name_path, "w") as file:
                file.write(json.dumps(data,indent=3))
            return data  

    #----------
    def update_dict_cache(self,file_name_path:str,key:str,func:Callable,**kwargs) -> dict:
        '''
        This function is intended to be used as the core of a decorator function.
        This function is for getting a single record that MIGHT be part of a bigger dict.
        The function first looks for the record in the dict (is given key present?). If that fails,
        we call the given function (typically an API call) to find the data elsewhere.
        We then (a) update the dict with the new record and (b) return the new record.
        '''
        # key = kwargs.pop('key')
        try:
            with open(file_name_path, "r") as file:
                existing_data = json.loads(file.read())
            #If the data we're looking for exists in the file:
            if key in existing_data.keys():
                return existing_data[key]
            #If the data is not in the file, update the file:
            else:
                new_data = func(self,key,**kwargs)
                existing_data.update(new_data)
                with open(file_name_path, "w") as file:
                    file.write(json.dumps(existing_data,indent=3))
        except:
            #If file interaction failed, it's likely because no file existed. In this case,
            #we just return the data since writing to file might be an incomplete record.
            message = f"Could not update cache: {file_name_path}"
            warn(message)
            return func(self,key,**kwargs)

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
            kwargs.update(json.dumps(kwargs['body']))

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
            raise Exception(f"API call returned non-200 response. Response data: {json.loads(http_response.data)}")

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



#==========
class RegisterNewAgent(HttpConnection,GameConfig):
    """
    This class registers a new agent. This class is a bit of an exception to the others used in the game
    in that the methods in this class must be run first before any other game data (e.g., API key) is initialized.
    For that reason, this class holds some repeated values and doesn't rely on the more complex classes.
    """

    #----------
    def __init__(self):
        pass
        
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
        # config.read(self.account_config_filepath)

        credentials = config['ACCOUNT_CREDENTIALS'] = {
            'account_id':new_agent_response['data']['agent']['accountId']
            ,'callsign':new_agent_response['data']['agent']['symbol']
            ,'key_encrypted':encrypted_key_bytes.decode() #converting bytes to string with .decode()
        }

        #(Over)writing credentials to local file:
        with open(self.account_config_filepath, 'w') as configfile:
            config.write(configfile)

