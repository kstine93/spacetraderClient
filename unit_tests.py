from src.utilities import *
from src.agent import *


#----------
def test_save_agent_metadata_locally():
    response = {
         'data':{
              'token':'test_token'
              ,'agent':{
                   'accountId':'test_id'
                   ,'symbol':'test_callsign'
              }
         }
    }

    save_agent_metadata_locally(response,local_cfg_filepath="./test_account_info.cfg")


#----------
def test_decrypt_and_store_api_key_locally():
    decrypt_and_store_api_key_locally(local_key_filepath='./test.txt')


#----------
if __name__ == "__main__":
    test_save_agent_metadata_locally()
    test_decrypt_and_store_api_key_locally()