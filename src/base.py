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

from urllib3 import PoolManager
from .utilities.basic_utilities import prompt_user_password
from .utilities.crypt_utilities import password_decrypt
from configparser import ConfigParser


#==========
class HttpConnection:
    """
    Generic class for making API requests
    """
    conn:PoolManager | None = None
    

    def __init__(self):
        self.conn = PoolManager()

    def post_req():
        pass

    def get_req():
        pass

    def patch_req():
        pass

#==========
class SpaceTraderConnection(HttpConnection):
    """
    Class that enables API usage for the SpaceTrader game
    - primarily by loading and storing api and base url of endpoint
    """
    local_cfg_filepath:str = "./account_info.cfg"
    api_key: str | None = None
    base_url:str = "https://api.spacetraders.io/v2"
    
    #----------
    def __init__(self):
        super()
        self.load_api_key(self.local_cfg_filepath,self.local_key_filepath)

    #----------
    def load_api_key(self,cfg_path:str) -> None:
        '''Purpose: Decrypt API key and store it locally so that we can use it for future API calls'''
        config = ConfigParser()
        config.read(cfg_path)
        encrypted_key = config['ACCOUNT_CREDENTIALS']['key_encrypted']

        password = prompt_user_password("Please enter password to decrypt your API key:")

        decrypted_key_bytes = password_decrypt(encrypted_key, password)
        self.api_key = decrypted_key_bytes.decode() #converting to string

