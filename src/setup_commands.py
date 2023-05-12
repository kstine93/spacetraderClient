#----------
# Goals of this file:
# 1. List initial commands for starting Spacetraders game
#----------

import urllib3
import json
import configparser
from .utilities.basic_utilities import *

#----------
def register_new_agent(agent_callsign,faction) -> dict:

    #Register a new player with the game.
    #Returns dictionary with agent metadata (as well as other ship + contract information)
    http = urllib3.PoolManager()

    body = {
        'symbol':agent_callsign
        ,'faction':faction
    }

    response = http.request(
        method="POST"
        ,url='https://api.spacetraders.io/v2/register'
        ,headers={'Content-Type': 'application/json'}
        ,body=json.dumps(body)
    )
    return bytes_to_dict(response)


#----------
def save_agent_metadata_locally(new_agent_response:dict
                                ,local_cfg_filepath:str = "./account_info.cfg") -> None:
    
    #Receives dictionary response from registering a new agent.
    #Saves account ID, callsign, and encrypted API key in a local file.

    encrypted_key_bytes = encrypt_api_key(new_agent_response['data']['token'])

    config = configparser.ConfigParser()
    config.read(local_cfg_filepath)

    credentials = config['ACCOUNT_CREDENTIALS'] = {
        'account_id':new_agent_response['data']['agent']['accountId']
        ,'callsign':new_agent_response['data']['agent']['symbol']
        ,'key_encrypted':encrypted_key_bytes.decode() #converting bytes to string with .decode()
    }

    #(Over)writing credentials to local file:
    with open(local_cfg_filepath, 'w') as configfile:
        config.write(configfile)


#----------
def decrypt_and_store_api_key_locally(local_cfg_filepath:str = "./account_info.cfg"
                                      ,local_key_filepath:str = "./unencrypted_key.txt") -> None:
    
    '''Purpose: Decrypt API key and store it locally in a non-tracked file so that we can use it for gaming'''
    config = configparser.ConfigParser()
    config.read(local_cfg_filepath)

    encrypted_key = config['ACCOUNT_CREDENTIALS']['key_encrypted']
    decrypted_key_bytes = decrypt_api_key(encrypted_key)
    decrypted_key = decrypted_key_bytes.decode() #converting to string
    with open(local_key_filepath, 'w') as file:
        file.write(decrypted_key)