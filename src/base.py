"""
This file contains the base data + classes used as a foundation for most of the rest of the game.
This file also contains a class for registering a new agent and thereby setting up a new game.
"""

#==========
import json
from configparser import ConfigParser
from time import sleep
from urllib3 import PoolManager, HTTPResponse
from .utilities.basic_utilities import get_user_password,bytes_to_dict,dict_to_bytes
from .utilities.crypt_utilities import password_encrypt,password_decrypt
from .utilities.config_utilities import get_config,update_config_file
from .utilities.custom_types import SpaceTraderResp

#For debugging HTTP requests:
# import http.client
# http.client.HTTPConnection.debuglevel=5

#===========
#Basic functions to get game config data:

#----------
config_path = "./account_info.cfg"
config = get_config(config_path)

#----------
def get_config_encrypted_key() -> str:
    return config["ACCOUNT_CREDENTIALS"]["key_encrypted"]

#----------
def get_config_callsign() -> str:
    return config["ACCOUNT_CREDENTIALS"]["callsign"]

#----------
def get_config_cache_path() -> str:
    return config["CACHE"]["path"]

#----------
def get_config_url() -> str:
    return config["API"]["url"]


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
            print(kwargs.get('body'))

        return self.conn.request(
            method=method
            ,url=url
            ,**kwargs
        )

#==========
class SpaceTraderConnection:
    """
    Class that enables API usage for the SpaceTrader game
    - primarily by loading and storing api and base url of endpoint
    """
    #----------
    http_conn = HttpConnection()
    callsign:str | None = None
    encrypted_key: str | None = None

    api_key: str | None = None
    default_header: dict = {"Accept": "application/json","Content-Type":"application/json"}
    base_url:str | None = None

    base_cache_path:str | None = None

    #----------
    def __init__(self):
        #Loading in config which has basic information on player:
        self.callsign = get_config_callsign()
        self.encrypted_key = get_config_encrypted_key()
        self.base_url = get_config_url()
        self.base_cache_path = get_config_cache_path()

        try:
            self.load_api_key()
            self.default_header.update({"Authorization" : "Bearer " + self.api_key})
        except Exception as e:
            msg = f"Error in loading API key. Please check API key at file path {config_path}"
            raise Exception(msg) from e

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
    def stc_http_request(self, method:str, url:str, **kwargs) -> SpaceTraderResp:
        """Wrapper for HTTP get - implements spacetrader-specific handling of response"""
        http_response = self.http_conn.http_request(method=method
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
class RegisterNewAgent:
    """
    This class registers a new agent. This class is a bit of an exception to the others used
    in the game in that the methods in this class must be run first before any other game data
    (e.g., API key) is initialized. For that reason, this class holds some repeated values and
    doesn't rely on the more complex classes.
    """
    #----------
    config_path = config_path
    http_conn = HttpConnection()
    base_url: str | None = None
    config: ConfigParser | None = None

    #----------
    def __init__(self):
        self.config = get_config(config_path)
        self.base_url = get_config_url()

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

        http_response = self.http_conn.http_request("POST",url=url,body=body,headers=headers)
        data = bytes_to_dict(http_response.data)
        self.save_agent_metadata_locally(data)

    #----------
    def save_agent_metadata_locally(self, new_agent_response:dict) -> None:
        """
        Receives dictionary response from registering a new agent. Saves account ID, callsign,
        and encrypted API key in a local file. This local file is the basis for which player
        is playing the game.
        """
        prompt = "Please enter password to encrypt your API key:"
        password = get_user_password(prompt=prompt,password_name="SPACETRADER_PASSWORD")

        bytes_token = dict_to_bytes(new_agent_response['data']['token'])

        encrypted_key_bytes = password_encrypt(bytes_token,password)

        data = {
            'account_id':new_agent_response['data']['agent']['accountId']
            ,'callsign':new_agent_response['data']['agent']['symbol']
            ,'key_encrypted':encrypted_key_bytes.decode()
        }

        update_config_file(self.config_path,section="ACCOUNT_CREDENTIALS",data=data)

