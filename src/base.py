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

    api_key: str | None = None
    default_header: dict = {"Accept": "application/json"}
    base_url: str = "https://api.spacetraders.io/v2"

    cache_file_prefix: str | None = None
    
    #----------
    def __init__(self):
        HttpConnection.__init__(self)
        try:
            self.load_api_key(self.local_cfg_filepath)

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





