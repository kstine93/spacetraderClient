"""
Basic functional programming utilities portable across applications
"""

#==========
import json
import getpass
# from .crypt_utilities import *
from typing import Callable

#==========
def bytes_to_dict(bytes_obj:bytes,format:str = 'utf-8') -> dict:
    return json.loads(bytes_obj.decode(format))

#==========
def dict_to_bytes(dict_obj:dict, format:str = 'utf-8') -> bytes:
    return dict_obj.encode(format)

#==========
def prompt_user_password(prompt:str) -> str:
    return getpass.getpass(prompt)
