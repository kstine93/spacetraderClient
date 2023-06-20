"""
This file contains the base data + classes used as a foundation for most of the rest of the game.
This file also contains a class for registering a new agent and thereby setting up a new game.
"""

#==========
import logging
import yaml
from time import sleep
from typing import Generator
from requests import request
from requests.models import Response
from .utilities.basic_utilities import get_user_password,dict_to_bytes,get_keys_in_file,get_dict_from_file
from .utilities.crypt_utilities import password_encrypt,password_decrypt
from .utilities.custom_types import SpaceTraderResp

#For debugging HTTP requests:
# import http.client
# http.client.HTTPConnection.debuglevel=5


#===========
class SpaceTraderConfigSetup:
    """Class to interact with the configurtion file which provides game details"""
    config_path = "./gameinfo.yaml"
    config:dict

    #----------
    def __init__(self):
        self.reload_config()

    #----------
    def reload_config(self) -> None:
        with open(self.config_path, "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    #----------
    def get_encrypted_key(self,callsign:str) -> str:
        agents = self.config['agents']['all_agents']
        item = next((item for item in agents if item['callsign'] == callsign),False)
        return item['key_encrypted']

    #----------
    def get_callsign(self) -> str:
        return self.config['agents']['current']

    #----------
    def get_cache_path(self) -> str:
        return self.config["cache"]["path"]

    #----------
    def get_api_url(self) -> str:
        return self.config["api"]["url"]

    #----------
    def write_to_file(self) -> None:
        """Write config to file"""
        with open(self.config_path, 'w') as configfile:
            yaml.dump(self.config,configfile)

    #----------
    def get_config(self) -> dict:
        return self.config

    #----------
    def get_all_callsigns(self) -> list[str]:
        agents = self.config['agents']['all_agents']
        return [item['callsign'] for item in agents]

    #----------
    def set_new_current_agent(self,callsign:str) -> None:
        self.config['agents']['current'] = callsign
        self.write_to_file()

    #----------
    def add_new_agent(self,callsign:str,encrypted_key:str) -> None:
        data = {callsign:encrypted_key}
        self.config['agents']['all_agents'].append(data)
        self.write_to_file()


#==========
class SpaceTraderConnection:
    """
    Class that enables API usage for the SpaceTrader game
    - primarily by loading and storing api and base url of endpoint
    """
    #----------
    config_setup = SpaceTraderConfigSetup()

    callsign:str
    encrypted_key: str

    api_key: str
    default_header: dict = {"Accept": "application/json","Content-Type":"application/json"}
    base_url:str

    base_cache_path:str

    #----------
    def __init__(self):
        #Loading in config which has basic information on player:
        self.callsign = self.config_setup.get_callsign()
        self.encrypted_key = self.config_setup.get_encrypted_key(self.callsign)
        self.base_url = self.config_setup.get_api_url()
        self.base_cache_path = self.config_setup.get_cache_path()

        try:
            self.load_api_key()
            self.default_header.update({"Authorization" : "Bearer " + self.api_key})
        except Exception as e:
            msg = f"Error in loading API key. Please check API key at file path {self.config_setup.config_path}"
            raise Exception(msg) from e

    #----------
    def load_api_key(self) -> None:
        """Purpose: Decrypt API key and store it locally so that we can use it
        for future API calls"""
        password = get_user_password(prompt="Please enter password to decrypt your API key:"
                                     ,password_name="SPACETRADER_PASSWORD")
        bytes_key = self.encrypted_key.encode("utf-8")
        decrypted_key_bytes = password_decrypt(bytes_key, password)
        self.api_key = decrypted_key_bytes.decode() #converting to string

    #----------
    def response_ok(self,response:SpaceTraderResp) -> bool:
        """Check if API response resulted in a valid response (TRUE) or not (FALSE).
        Print and log error responses if they exist"""
        if "error" in response['http_data'].keys():
            print(response['http_data']['error']['message'])
            logging.warn(f"API returned error: {response['http_data']['error']['message']}")
            return False
        return True

    #----------
    def repackage_http_response(self,http_response:Response) -> SpaceTraderResp:
        """Transforms http_response (sometimes in a complex format) to simple dictionary."""
        packet = {}
        packet['http_status'] = http_response.status_code
        try:
            packet['http_data'] = http_response.json()
        except:
            packet['http_data'] = {}
            logging.info(f"Could not parse response data for {http_response.url}")
        return packet

    #----------
    def get_system_from_waypoint(self,waypoint:str) -> str:
        """In Alpha version of the game, the system is the first 7 characters of the waypoint.
        Rather than pass both values around, this derives system from waypoint"""
        return waypoint[0:7]

    #----------
    def stc_http_request(self, method:str, url:str, **kwargs) -> SpaceTraderResp:
        """Wrapper for HTTP get - implements spacetrader-specific handling of response"""
        http_response = request(
            method=method
            ,url=url
            ,headers=self.default_header
            ,**kwargs
        )

        return self.repackage_http_response(http_response)

    #----------
    def stc_get_paginated_data(self,method:str,url:str,page:int=1,**kwargs) -> Generator[SpaceTraderResp,None,None]:
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
    config_setup = SpaceTraderConfigSetup()
    base_url: str

    #----------
    def __init__(self):
        self.base_url = self.config_setup.get_config_url()

    #----------
    def register_new_agent(self, agent_callsign:str, faction:str = "COSMIC") -> None:
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

        http_response = request("POST",url=url,body=body,headers=headers)
        data = http_response.json()
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

        callsign = new_agent_response['data']['agent']['symbol']
        encrypted_key = encrypted_key_bytes.decode()

        self.config_setup.add_new_agent(callsign,encrypted_key)

