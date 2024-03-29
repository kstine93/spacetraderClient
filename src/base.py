"""
This file contains the base data + classes used as a foundation for most of the rest of the game.
This file also contains a class for registering a new agent and thereby setting up a new game.
"""

#==========
import logging
import json
import yaml
import re
from time import sleep
from typing import Generator
from requests import request
from requests.models import Response
from .utilities.basic_utilities import get_user_password,dict_to_bytes
from .utilities.crypt_utilities import password_encrypt,password_decrypt
from .utilities.custom_types import SpaceTraderResp

#For debugging HTTP requests:
# import http.client
# http.client.HTTPConnection.debuglevel=5


#===========
class SpaceTraderConfigSetup:
    """Class to interact with the configurtion file which provides game details
    NOTE: This class purposefully does not hold stateful data as class attributes because
    config data can change mid-game (most commonly after creating new agents"""

    config_path = "./gameinfo.yaml"

    #----------
    def __init__(self):
        pass

    #----------
    def __get_config(self) -> None:
        with open(self.config_path, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    #----------
    def get_encrypted_key(self,callsign:str) -> str:
        config = self.__get_config()
        agents = config['agents']['all_agents']
        item = next((item for item in agents if item['callsign'] == callsign),False)
        return item['key_encrypted']

    #----------
    def get_current_player(self) -> str:
        config = self.__get_config()
        return config['agents']['current']

    #----------
    def get_cache_path(self) -> str:
        config = self.__get_config()
        return config["cache"]["path"]

    #----------
    def get_api_url(self) -> str:
        config = self.__get_config()
        return config["api"]["url"]

    #----------
    def get_config(self) -> dict:
        config = self.__get_config()
        return config

    #----------
    def get_all_callsigns(self) -> list[str]:
        config = self.__get_config()
        agents = config['agents']['all_agents']
        return [item['callsign'] for item in agents] if agents else []

    #----------
    def set_new_current_agent(self,callsign:str) -> None:
        config = self.__get_config()
        config['agents']['current'] = callsign
        self.write_to_file(config)

    #----------
    def add_new_agent(self,callsign:str,encrypted_key:str) -> None:
        config = self.__get_config()
        data = {
            "callsign":callsign
            ,"key_encrypted":encrypted_key
            }
        if config['agents']['all_agents']:
            config['agents']['all_agents'].append(data)
        else:
            config['agents']['all_agents'] = [data]
        self.write_to_file(config)
        self.set_new_current_agent(callsign)

    #----------
    def remove_agent_details(self,callsign:str) -> None:
        '''Note: This method only removes the reference to the player in the local file.
        Currently, there is no way to 'delete' a player from the game on the game server.'''
        config = self.__get_config()
        agents = config['agents']['all_agents']
        if agents:
            # print(config['agents']['all_agents'])
            filtered_agents = [rec for rec in agents if rec['callsign'] != callsign]
            config['agents']['all_agents'] = filtered_agents
            self.write_to_file(config)

    #----------
    def write_to_file(self,config:dict) -> None:
        """Write config to file"""
        with open(self.config_path, 'w') as configfile:
            yaml.dump(config,configfile)


#==========
class SpaceTraderConnection:
    """
    Class that enables API usage for the SpaceTrader game
    - primarily by loading and storing api and base url of endpoint
    """
    #----------
    config_setup = SpaceTraderConfigSetup()

    callsign:str

    api_key: str
    default_header: dict = {"Accept": "application/json","Content-Type":"application/json"}
    base_url:str

    base_cache_path:str

    #----------
    def __init__(self,given_api_key:str=None):
        self.base_url = self.config_setup.get_api_url()
        self.base_cache_path = self.config_setup.get_cache_path()

        #If an api key is provided, use that to start the game. Otherwise, find the current player
        #in the local file and initialize the game using that information.
        if given_api_key != None:
            self.api_key = given_api_key
        else:
            player = self.config_setup.get_current_player()
            try:
                encrypted_key = self.config_setup.get_encrypted_key(player)
                self.api_key = self.__decrypt_api_key(encrypted_key)
            except Exception as e:
                msg = f"Error in loading API key. Please check API key at file path {self.config_setup.config_path}"
                raise Exception(msg) from e

        self.default_header.update({"Authorization" : "Bearer " + self.api_key})
        self.callsign = self.get_agent()['symbol']

    #----------
    def __decrypt_api_key(self,encrypted_key:str) -> None:
        """Purpose: Decrypt API key and store it locally so that we can use it
        for future API calls"""
        password = get_user_password(prompt="Please enter password to decrypt your API key: "
                                     ,password_name="SPACETRADER_PASSWORD",double_entry=False)
        bytes_key = encrypted_key.encode("utf-8")
        decrypted_key_bytes = password_decrypt(bytes_key, password)
        return decrypted_key_bytes.decode() #converting to string

    #----------
    def get_agent(self) -> dict:
        """Get basic information about agent: callsign, account ID, faction, HQ, etc."""
        url = f"{self.base_url}/my/agent"
        response = self.stc_http_request(method="GET",url=url)
        if not self.response_ok(response): raise Exception(response)
        return response['http_data']['data']

    #----------
    def response_ok(self,response:SpaceTraderResp) -> bool:
        """Check if API response resulted in a valid response (TRUE) or not (FALSE).
        Print and log error responses if they exist"""
        if "error" in response['http_data'].keys():
            print(response['http_data']['error']['message'])
            # logging.warning(f"API returned error: {response['http_data']['error']['message']}")
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
        """In Alpha version of the game, the system is the first part of the waypoint, before the
        second dash (e.g., waypoint = 'X1-Z7-45360X', system = 'X1-Z7').
        Rather than pass both values around, this derives system from waypoint"""
        match = re.match(r"^[\w]+-[\w]+",waypoint)
        return match.group()

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
        self.base_url = self.config_setup.get_api_url()

    #----------
    def register_new_agent(self, agent_callsign:str, faction:str = "COSMIC") -> bool:
        """
        Register a new player with the game.
        Saves agent data locally if the registration was a success. If not, prints out the error and
        returns a 'False' value to abort
        """
        data = {
            'faction':faction
            ,'symbol':agent_callsign
        }
        headers = {"Accept": "application/json","Content-Type":"application/json"}
        url = self.base_url + "/register"

        http_response = request("POST",url=url,data=json.dumps(data),headers=headers)
        data = http_response.json()

        if "error" in data.keys():
            print(data['error']['message'])
            return False
        else:
            token = data['data']['token']
            callsign = data['data']['agent']['symbol']
            self.save_agent_metadata_locally(token=token,callsign=callsign)
            return True

    #----------
    def save_agent_metadata_locally(self, token:dict, callsign:str) -> None:
        """
        Receives dictionary response from registering a new agent. Saves account ID, callsign,
        and encrypted API key in a local file. This local file is the basis for which player
        is playing the game.
        """
        prompt = "Please enter password to encrypt your API key: "
        password = get_user_password(prompt=prompt,password_name="SPACETRADER_PASSWORD",double_entry=True)

        bytes_token = dict_to_bytes(token)
        encrypted_key_bytes = password_encrypt(bytes_token,password)
        encrypted_key = encrypted_key_bytes.decode()

        self.config_setup.add_new_agent(callsign,encrypted_key)

