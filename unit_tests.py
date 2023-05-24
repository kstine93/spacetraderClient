from src.utilities import *
from src.agent import *
from src.contracts import *
from src.factions import *
from src.systems import *

from collections import Counter
from os import listdir,remove,fsdecode

'''
How to test 'list' commands?
1. These commands should really be re-named. They're no longer about getting a full list, but rather refreshing the cache.
2. I think the only measure of success is whether the file in the right folder has been FULLY UPDATED.
    2a. I can see 'last edited' probably, but that feels weird.
    2b. What about deleting the files and then re-creating them and seeing if it works?
        2bi. Since this operation is really intensive, I should probably test infrequently - maybe have a separate test suite.
'''


#-------
#UTILITIES
def assert_equal_dict_keys(data:dict,test_keys:list) -> None:
    assert Counter(data.keys()) == Counter(test_keys)

def empty_directory(dir_path:str):
    for file in listdir(dir_path):
        file_path = f"{dir_path}/{fsdecode(file)}"
        remove(file_path)


#---------
#--AGENT--
#---------
callsign = "AMBROSIUS-RITZ"
agent_schema = ['accountId','symbol','headquarters','credits','startingFaction']
agent_folder = f"./gameData/agents/"
agent = Agent()

#Reloading local cache
empty_directory(agent_folder)
assert_equal_dict_keys(agent.get_agent_details(callsign),agent_schema)
#Pulling from local cache:
assert_equal_dict_keys(agent.get_agent_details(callsign),agent_schema)


#-------------
#---FACTIONS--
#-------------
faction_schema = ["symbol","name","description","headquarters","traits","isRecruiting"]
faction_filepath = "./gameData/factions/"
faction = Factions()

#Reloading local cache
empty_directory(faction_filepath)
assert_equal_dict_keys(faction.get_faction("VOID"),faction_schema)
#pulling from local cache:
assert_equal_dict_keys(faction.get_faction("VOID"),faction_schema)

#TEST_LIST_FACTIONS() !!!


#-------------
#--CONTRACTS--
#-------------
contract = Contracts()
contract_name = "clhz8vpb5132os60d068nfihj"
contracts_filepath = "./gameData/contracts/"
contract_schema = ['id','factionSymbol','type','terms','accepted','fulfilled','expiration','deadlineToAccept']

#Reloading local cache
empty_directory(contracts_filepath)
assert_equal_dict_keys(contract.get_contract(contract_name),contract_schema)
#pulling from local cache:
assert_equal_dict_keys(contract.get_contract(contract_name),contract_schema)

#TEST_LIST_CONTRACTS() !!!


#-----------
#--SYSTEMS--
#-----------
system = Systems()
system_name = "X1-AQ83"
systems_filepath = "./gameData/systems"
system_schema = ['symbol','sectorSymbol','type','x','y','waypoints','factions']

#Not emptying systems directory - takes too long to re-populate.
assert_equal_dict_keys(system.get_system(system_name),system_schema)

#TEST_LIST_SYSTEMS() !!!




print("all tests completed successfully")

