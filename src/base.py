#Generic class for interacting with API
#---------
#NOTE: Is there a possibility to set up my urllib3 connection pool more efficiently? I'm not sure how it's currently
#setting up and using the connection pool - it would be nice if this were centrally managed - so that I could
#conceivably centrally know how many requests I'm sending.


#NOTE: What am I trying to accomplish here?
# I will be making API calls in lots of places - I want these calls to use a central structure + connection pool to
# make this easier to update and maintain - I want my calls to implement this structure rather than defining their
# own structure.
# So, I think it's fine to define a class and have each of my scripts create an instance.... BUT maybe not - there's no
# data I need to keep consistent. What about just creating a utilities-like function here that does what I want?
# Do I really need a class?
# >> I do like the idea of each class instance coming with a 'connection' - so that I can use it for many functions.
# I will do this- and keep the connection pool as a global variable I can use for multiple calls!
# Then, I can actually extend this class to be child classes that have more specific functions - so my functions are
# nicely packaged in classes rather than loose.

from urllib3 import PoolManager, HTTPResponse
from .utilities.basic_utilities import *
from .utilities.crypt_utilities import password_decrypt
from configparser import ConfigParser
import json
from typing import Callable

def get_it():
    config = ConfigParser()
    config.read("./account_info.cfg")
    return config['ACCOUNT_CREDENTIALS']['callsign']

#==========
class SpaceTraderCacheManager:
    """Generic class for loading data to/from a cache or local file system"""
    # TODO: Make a more generic version of this class to be the parent class.
    # NOTE: Is it possible to initialize the inner decorator function in this generic class, and then initialize
    # the outer decorator function (which takes in the parameters) in one of the child classes?
    # If that works, it might even be possible to initialize the outer decorator function in the class it's being used in
    # (e.g., Agent) and thereby be able to use variables initialised in the class (file_path) and (file_name)
    #----------
    local_cfg_filepath:str = "./account_info.cfg"
    base_cache_path:str = "./gameData/"
    base_cache_file_name:str = "test3" #get_it()
    test5 = "CM_value"

    #----------
    def __init__(self):
        pass
        #Putting 'Callsign' as the default name of cache files:
        config = ConfigParser()
        config.read(self.local_cfg_filepath)
        self.base_cache_file_name = config['ACCOUNT_CREDENTIALS']['callsign']


    # #----------
    # def transform_file_name(self,input:str):
    #     '''
    #     Function to ensure that file names are consistent across child classes.
    #     Currently we're using a unique key as a unique identifier of resources belonging to a specific
    #     account (this is how SpaceTraders does it). This is accessible to all child classes, so they can
    #     feed this to this method and get a transformed string in return that serves as a file name.
    #     Currently, this is just the first 10 characters of the unique key.
    #     '''
    #     return input[0:9]
    
    def read_dict_cache_v2(self,file_name_path:str,func:Callable,**kwargs):
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


    def decorator_v2(func: Callable):

        # TODO: Make this function nicer:
        # 1. Decide where to put this code - in a higher-level class?
        # 2. Look if I need more versions of this (e.g., for appending rather than overwriting files) 
        def wrapper(self, **kwargs):
            for key in kwargs:
                print(key)
            # print("Y_"+self.test5)
            # print("Y_"+self.cache_path)
            #For this command below, I got an error that 'Agent' doesn't have this variable.
            # Is it looking in the Agent class? If yes, it's also pulling from the parent class for local_cfg_filepath...
            #print("X_"+self.base_cache_filename) 
            new_path = self.cache_path + self.test5 + ".json"
            print(new_path)
            try:
                with open(new_path, "r") as file:
                    return json.loads(file.read())

            except:
                data = func(self, **kwargs)
                with open(new_path, "w") as file:
                    file.write(json.dumps(data,indent=3))
                return data
            
        return wrapper


    #----------
    def get_dict_cache(path:str,file_name:str):
        """
        Decorator function.
        Intended to be used prior to retrieving data from a remote source.
        If a relevant .json file in the provided file path, it returns the data in the file as a dictionary.
        If this operation fails, the inner function is called (which MUST return a dict object).
        This function then saves the results of that function call as the missing JSON file and returns the value.
        """
        print("x_"+path)
        print("x_"+file_name)
        #Additional wrapping function allows us to pass parameters to decorator.
        def decorator(func: Callable) -> dict:

            # TODO: Make this function nicer:
            # 1. Decide where to put this code - in a higher-level class?
            # 2. Look if I need more versions of this (e.g., for appending rather than overwriting files) 
            def wrapper(self, **kwargs):
                print("Y_"+self.test5)
                print("Y_"+self.local_cfg_filepath)
                #For this command below, I got an error that 'Agent' doesn't have this variable.
                # Is it looking in the Agent class? If yes, it's also pulling from the parent class for local_cfg_filepath...
                #print("X_"+self.base_cache_filename) 
                new_path = path + file_name + ".json"
                print(new_path)
                try:
                    with open(new_path, "r") as file:
                        return json.loads(file.read())

                except:
                    data = func(self, **kwargs)
                    with open(new_path, "w") as file:
                        file.write(json.dumps(data,indent=3))
                    return data
                
            return wrapper
        return decorator

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
            kwargs.update(dict_to_str(kwargs['body']))

        return self.conn.request(
            method=method
            ,url=url
            ,**kwargs
        )


#==========
class SpaceTraderConnection(HttpConnection):
    """
    Class that enables API usage for the SpaceTrader game
    - primarily by loading and storing api and base url of endpoint
    """
    #----------
    local_cfg_filepath:str = "./account_info.cfg"

    test: str | None = None
    api_key: str | None = None
    default_header: dict = {"Accept": "application/json"}
    base_url: str = "https://api.spacetraders.io/v2"

    cache_file_prefix: str | None = None
    
    #----------
    def __init__(self):
        HttpConnection.__init__(self)
        try:
            self.load_api_key(self.local_cfg_filepath)
            self.test = self.api_key[0:9]
            self.default_header.update({"Authorization" : "Bearer " + self.api_key})
            self.cache_file_prefix = self.api_key[0:9] #First 10 characters used for file identification - totally arbitrary #.
        except Exception as e:
            raise e(f"Error in loading API key. Please check API key is present at file path {self.local_cfg_filepath}")

    #----------
    def load_api_key(self,cfg_path:str) -> None:
        '''Purpose: Decrypt API key and store it locally so that we can use it for future API calls'''
        config = ConfigParser()
        config.read(cfg_path)
        encrypted_key = config['ACCOUNT_CREDENTIALS']['key_encrypted']

        password = prompt_user_password("Please enter password to decrypt your API key:")
        decrypted_key_bytes = password_decrypt(encrypted_key, password)
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





