#Basic functional programming utilities
#Should all be portable across applications

import json
import getpass
from .crypt_utilities import *

#----------
def bytes_to_dict(bytes_obj:bytes,format:str = 'utf-8'):
    #Returns dictionary-like in bytes format as a Python dictionary
    return json.loads(bytes_obj.decode(format))

def dict_to_bytes(dict_obj:dict, format:str = 'utf-8'):
    return dict_obj.encode(format)

#----------
def prompt_user_password(prompt:str):
        return getpass.getpass(prompt)

# #----------
# def encrypt_api_key(input:str) -> bytes:
#     '''Simple wrapper for encryption with message'''
#     pw = getpass.getpass(prompt="Please enter password to encrypt your API key with:")
#     encrypted = password_encrypt(input.encode(), pw)
#     # decrypted = password_decrypt(encrypted,pw).decode()
#     # print(encrypted.decode())
#     # print(decrypted)
#     return encrypted

# #----------
# def decrypt_api_key(secret:bytes) -> bytes:
#     '''Simple wrapper for encryption with message'''
#     pw = getpass.getpass(prompt="Please enter password to decrypt your API key:")
#     return password_decrypt(secret, pw)

