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
from .custom_types import SpaceTraderResp
from warnings import warn
from os import fsdecode,listdir,path
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
    def attempt_cache_retrieval(self,file_path:str) -> dict:
        '''Attempts to get data as dictionary from file'''
        if path.exists(file_path):
            return self.get_dict_from_file(file_path)
        else:
            warn(f"no existing file at {file_path}. New file will be created.")
            return {}       

    #----------
    def custom_get_cache_dict(self,file_path:str,existing_data:dict,func:Callable,nested_key:str,**kwargs) -> dict:
        # #LOGIC #1:
        # existing_data = self.attempt_cache_retrieval(file_path)

        # #LOGIC #2:
        # if new_key in existing_data.keys():
        #     data = existing_data[new_key]
        # else:
        #     data = base_func(self,new_key)

        #LOGIC #1 + LOGIC #2:
        # data = get_system(system)
        
        #----------
        #LOGIC #3:

        #Get nested data:
        waypoint_list = existing_data['waypoints']
        #nested_data = filter(lambda waypoint_list: waypoint_list['symbol'] == nested_key, waypoint_list)

        #Check data with first record (arbitrarily chosen):
        test_record = waypoint_list[0]
        if set(['orbitals','traits','chart','faction']).issubset(test_record.keys()):
            #If nested data is there, return it:
            return waypoint_list
        else:
            #Update nested record
            retrieved_data = func(self)

            #Update existing record
            existing_data['waypoints'] = retrieved_data
            self.update_cache_dict(existing_data,file_path)
        #----------

        '''
        Generic:
        0. pass function to get data? (default: get file from path)
            0a. Upgraded: Pass keys to get into nested part?
        1. pass function to check logic (default: is new_key in data.keys())
            1a. Upgraded: Pass function to check logic.
        2. pass function to update data (default: existing_data.update(new_data))
        3. pass function for what to do if greater data structure (e.g., file, record) does not exist
                    (default: create new file)
            3a. Upgraded: get_record function call

        ------
        >> Let's make a dumb version that works for scan_waypoints and then we'll see
        about making it better
        '''

        # self.update_cache_dict(data,file_path)
        # return data[new_key]

    '''
    The logic that NEEDS to exist is:
    1. Check whether the file exists
        a. YES: get data from file
        b. NO: Initialize new data
    2. Check whether the record exists in data
        a. YES: ***Get record from data***
        b. NO: ***CALL GET_ FUNCTION TO GET BASE DATA***
    3. Check whether nested record matches criteria
        a. YES: ***Return existing nested record data[key][record]
        b. NO: ***CALL OTHER GET_ FUNCTION TO GET NESTED DATA***
            b1. ***update nested data***
            b2. update existing data
            b3. save to file
    '''

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
        existing_data = self.attempt_cache_retrieval(file_path)
        if new_key in existing_data.keys():
            return existing_data[new_key]
        else:
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
        existing_data = self.attempt_cache_retrieval(file_path)
        existing_data.update(data)
        self.write_dict_to_file(file_path,existing_data)

    # #----------
    # def OLD_get_cache_dict(self,file_path:str,func:Callable,new_key:str,**kwargs) -> dict:
    #     '''
    #     This function is intended to be used as the core of a decorator function.
    #     This function is for getting a single record that MIGHT be part of a bigger dict in the local cache.
    #     The function first looks for the record in the dict (is given key present?). If that fails because
    #     the cache file doesn't exist or the key is not present in the dict,
    #     we call the given function (typically an API call) to find the data elsewhere.
    #     We then pass the new data on to 'update_cache_dict' to update the cache.
    #     '''
    #     try:
    #         #Try to open local cache and return record. If this fails, pull from API:
    #         existing_data = self.get_dict_from_file(file_path)
    #         return existing_data[new_key]
    #     except (KeyError, FileNotFoundError):
    #         data = func(self,new_key)
    #         self.update_cache_dict(data,file_path)
    #         return data[new_key]

    # #----------
    # def OLD_update_cache_dict(self,data:dict,file_path:str) -> dict:
    #     '''
    #     This function updates a local cache file with a given dictionary. If the file exists,
    #     we load the file data, update it with the given dictionary, and re-write it. If the file
    #     doesn't exist, we make a new file with the dictionary as the sole entry.
    #     '''
    #     try:
    #         #Try to get file (but not sure it exists):
    #         existing_data = self.get_dict_from_file(file_path)
    #     except FileNotFoundError:
    #         #If getting file failed, we replace file:
    #         existing_data = {}
    #         warn(f"no existing file at {file_path}. New file will be created.")
    #     finally:
    #         existing_data.update(data)
    #         self.write_dict_to_file(file_path,existing_data) 

    #----------
    def update_nested_cache_dict(self,data:dict,file_path:str) -> dict:
        '''
        What do I want this function to do?
        The issue I'm facing is that I am receiving some data that is not a complete record- but instead a PIECE
        of a record. I want to store this piece in the appropriate place in the cache - which is NESTED in an existing record.
        My current code above treats each record as atomic - either we return the record or we update it IN FULL, but we're not
        editing a piece of it like I need to do here.
        How can I most gracefully update a PIECE of a record?
        Options:
        1. I create a custom function for updating PIECES of records (somehow passing the instructions for updating the record)
        2. I create another place where I pull in the full record from the 'get_' function, update it with the new data, and then
            send that to the normal update function (I kind of like this more - option #1 would be vulnerable to the record not
            existing, so it would need to operate like #2 anyway).

        Where should #2 exist? So, the operation is ONLY being done for the cache - I don't actually need the full updated record
        for the game. It would make most sense to be in the 'CacheManager' class.

        Hmmm, how could I maybe just adapt what I already have to handle nesting? That would be most elegant. The issue is that the
        existing functions I have treat each record as a monolith

        ---

        Note: For the existing function above for SYSTEMS, if a record exists, it's assumed to be complete.
        But this assumption is wrong for this new operation - even if a record exists in the file, it doesn't
        mean it's complete. AND we can't even check the existence of the nested key for SYSTEMS - because
        the waypoint data is an EXTENSION of the existing waypoint data - but the waypoint already exists.
        Man... So the basic logic I have doesn't even work - look for a key and return it if you find it. Rather, 
        the waypoint data is only 'complete' if it has certain keys WITHIN it....


        The logic that currently exists is:
        1. Check whether the file exists
            a. YES: get data from file
            b. NO: Initialize new data
        2. Check whether the record exists in data
            a. YES: Return existing data[key]
            b. NO: CALL FUNCTION TO GET DATA
                b1. update existing data
                b2. save to file.


        The logic that NEEDS to exist is:
        1. Check whether the file exists
            a. YES: get data from file
            b. NO: Initialize new data
        2. Check whether the record exists in data
            a. YES: ***Get record from data***
            b. NO: ***CALL GET_ FUNCTION TO GET BASE DATA***
        3. Check whether nested record matches criteria
            a. YES: ***Return existing nested record data[key][record]
            b. NO: ***CALL OTHER GET_ FUNCTION TO GET NESTED DATA***
                b1. ***update nested data***
                b2. update existing data
                b3. save to file

        This logic is weirdly similar to another decorator - we need some of the same operations
        (e.g., doing initial checks if file exists, and initializing if it doesn't + saving file)
        but the middle of the function is different - where we have to dive deeper into the data

        ---
        OK - so it looks like the #1 and #3 can be somewhat already accomplished by
        "update_cache_dict" - and the correct data just needs to be passed to it.
        SO: I just need to pass the correctly-updated data to this function
        
        To do that, I need to make a new 'get_cache_dict' function that can correctly retrieve
        and search for the data, update the data, and then pass it on.
        '''
        # #LOGICAL PIECE #1
        # if (fileExists):
        #     existing_data = get_data_from_file()
        # else:
        #     existing_data = {}
        
        # #LOGICAL PIECE #2
        # if new_key in existing_data.keys():
        #     my_data = existing_data[new_key]
        # else:
        #     get_base_func(self)

        # #LOGICAL PIECE #3
        # #NOTE: This piece of logic is custom - there's no way to generalize HOW the data is
        # #nested. This is likely another function I need to pass in - how to extract the nested record
        # #from the base record.
        # waypoint_list = my_data['waypoints']
        # nested_data = filter(lambda waypoint_list: waypoint_list['symbol'] == nested_key, waypoint_list)

        # #NOTE: This is where generic logical checks might not work - I'm not looking for an
        # #existing key, I might be doing something bespoke like seeing if certain keys exist
        # #in the nested structure.
        # #IDEA: What if I make a bet now that I will always be able to check if a record contains
        # #all EXPECTED keys - and that will be sufficient to test whether the record is complete
        # #and should be returned - or is incomplete and should be queried from the API.
        # #I can name this 'check_record_complete'
        # if check_record_complete(nested_data,['orbtals','traits','chart','faction']):
        #     #data already exists in cache:
        #     return nested_data
        # else:
        #     #Update nested data
        #     list_without_record = filter(lambda waypoint_list: waypoint_list['symbol'] != nested_key, waypoint_list)
        #     list_without_record.append(nested_data)
        #     existing_data['waypoints'] = list_without_record
        #     #Save to file
        #     self.write_dict_to_file(file_path,existing_data) 

        '''
        The 3rd part of the logic is definitely the hairiest - I can make no assumptions about how
        to access the nested data or update it (and to a lesser extent - how to check its completeness
        - see 'check_record_complete' comment above.)
        >> I want to start building this in the CacheManager and then figure out what needs to be
            done OUTSIDE of this class in a more bespoke way.
        '''

         

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
    default_header: dict = {"Accept": "application/json"
                            ,"Content-Type": "application/json"
                            }
    
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
    def repackage_http_response(self,http_response:HTTPResponse) -> SpaceTraderResp:
        '''Transforms http_response (sometimes in a complex format) to simple dictionary.'''
        packet = {
            'http_data':json.loads(http_response.data),
            'http_status':http_response.status
        }
        return packet    

    #----------
    def get_system_from_waypoint(self,waypoint:str) -> str:
        '''In Alpha version of the game, the system is the first 7 characters of the waypoint.
        Rather than pass both values around, this derives system from waypoint'''
        return waypoint[0:7]


    """
    NOTE: I'm not sure I need to raise exceptions when the API call fails.
    In the case that the API call fails for a technical reason (401, 500), raising this exception and stopping the program
    doesn't really give me any advantages.
    In the case that the API call fails for a valid reason (409 - ability cooldown in effect), then I absolutely want to handle
    that - and at a higher level where I can interpret what this means for a particular API call.
    """
    # #----------
    # def stc_http_response_checker(self, http_response:HTTPResponse) -> bool:
    #     """Checks general success of the SpaceTrader API call and raises errors/warnings if a failure was found."""  
    #     #NOTE: Expand this as needed if we want custom handling of certain errors across all SpaceTrader endpoints.
    #     if http_response.status in [200,201]:
    #         return True
    #     else:
    #         msg = f"API call returned error response: {http_response.status}. Response data: {http_response.data.decode('utf-8')}"
    #         raise Exception()

    #----------
    def stc_http_request(self, method:str, url:str, **kwargs) -> SpaceTraderResp:
        """Wrapper for HTTP get - implements spacetrader-specific handling of response"""

        http_response = self.http_request(method=method
                                          ,url=url
                                          ,headers=self.default_header
                                          ,**kwargs)
        #If response is o.k., return
        #if self.stc_http_response_checker(http_response):
        return self.repackage_http_response(http_response)

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

        config['ACCOUNT_CREDENTIALS'] = {
            'account_id':new_agent_response['data']['agent']['accountId']
            ,'callsign':new_agent_response['data']['agent']['symbol']
            ,'key_encrypted':encrypted_key_bytes.decode()
        }

        #(Over)writing credentials to local file:
        with open(self.account_config_filepath, 'w') as configfile:
            config.write(configfile)

