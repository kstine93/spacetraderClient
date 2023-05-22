"""
Basic functional programming utilities portable across applications
"""

#==========
import json
import getpass
from typing import Callable

#==========
def bytes_to_dict(bytes_obj:bytes,format:str = 'utf-8') -> dict:
    return json.loads(bytes_obj.decode(format))

#==========
def dict_to_bytes(dict_obj:dict, format:str = 'utf-8') -> bytes:
    return dict_obj.encode(format)

#==========
def prompt_user_password(prompt:str) -> str:

    #TEMPORARY - FOR DEVELOPMENT:
    #Returning password stored as shell variable so
    #I don't have to keep entering the password to decrypt the API key...
    from os import getenv
    return getenv('SPACETRADER_PASSWORD')

    #return getpass.getpass(prompt)
