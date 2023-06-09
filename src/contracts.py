"""
Data and functions related for interacting with the 'contracts' endpoint of the Spacetrader API
"""
#==========
from typing import Callable
from .base import SpaceTraderConnection
from .utilities.custom_types import SpaceTraderResp
from .utilities.basic_utilities import attempt_dict_retrieval
from .utilities.cache_utilities import dict_cache_wrapper, update_cache_dict

#==========
class Contracts:
    """
    Class to query and edit game data related to contracts.
    """
    #----------
    base_url:str
    cache_path: str
    cache_file_name: str
    stc = SpaceTraderConnection()

    #----------
    def __init__(self):
        self.base_url = self.stc.base_url + "/my/contracts"
        #Using callsign as file name so contract files are associated with a particular account:
        self.cache_path = f"{self.stc.base_cache_path}contracts/{self.stc.callsign}.json"

    def mold_contract_dict(self,response:SpaceTraderResp) -> dict:
        '''Index into response dict from API to get contract data in common format'''
        if not self.stc.response_ok(response): raise Exception(response)
        data = response['http_data']['data']
        return {data['id']:data}

    #----------
    def cache_contracts(func: Callable) -> Callable:
        """
        Wrapper for an external, generic caching system.
        Passes a file path created from system variables and the 'contract' argument of the
        target function as values to the caching system to use in caching the data.
        Target function and its needed arguments (self,contract) also passed on.
        """
        def wrapper(self,contract:str):
            path = self.cache_path
            #Reminder: (func) and (self,faction) are being passed as args to nested functions:
            return dict_cache_wrapper(file_path=path,key=contract)(func)(self,contract)
        return wrapper

    #----------
    def reload_contracts_in_cache(self,page:int=1) -> None:
        """Force-updates all contracts data in cache with data from the API"""
        for contract_list in self.stc.stc_get_paginated_data("GET",self.base_url,page):
            for con in contract_list["http_data"]["data"]:
                transformed_con = {con['id']:con}
                update_cache_dict(transformed_con,self.cache_path)

    #----------
    #NOTE: Testing on June 5 resulted in an API call for reload_contracts below which resulted in
    #NO CONTRACTS - I guess my contract can technically expire (or be fulfilled) and this can
    #result in NO contracts being loaded in - even if reload_contracts works perfectly.
    #TODO: Make this function below prettier.
    def list_all_contracts(self) -> dict:
        """Get all contracts associated with the agent"""
        data = attempt_dict_retrieval(self.cache_path)
        if not data:
            self.reload_contracts_in_cache()
            #If no data is returned a 2nd time, it means no data is avaiable.
            data = attempt_dict_retrieval(self.cache_path)
        return data

    #----------
    #@cache_contracts
    def get_contract(self,contract:str) -> dict:
        """Get information about a specific contract"""
        url = self.base_url + "/" + contract
        response = self.stc.stc_http_request(method="GET",url=url)
        if not self.stc.response_ok(response): return {}
        #Transforming returned data to be compatible with contracts dict:
        data = self.mold_contract_dict(response)
        return data

    #----------
    def accept_contract(self,contract:str) -> dict:
        """Accept an in-game contract from the list of available contracts"""
        url = f"{self.base_url}/{contract}/accept"
        response = self.stc.stc_http_request(method="POST",url=url)
        if not self.stc.response_ok(response): return {}
        #Transforming returned data to be compatible with contracts dict:
        data = response['http_data']['data']['contract']
        data = {data['id']:data}
        update_cache_dict(data,self.cache_path)
        return data

    #----------
    def deliver_contract(self,contract:str,ship:str,item:str,quantity:int) -> dict:
        """Deliver a portion of the resources needed to fulfill a contract"""
        url = f"{self.base_url}/{contract}/deliver"
        body = {
            'shipSymbol':ship
            ,'tradeSymbol':item
            ,'units':quantity
        }
        response = self.stc.stc_http_request(method="POST",url=url,json=body)
        #NOTE: This method also returns a 'cargo' object which represents the type and quantity
        #of resource which was delivered. I could pass this object to my 'fleet' class to update
        #the quantity of the resource for the ship which was delivering this contract.

        #Transforming returned data to be compatible with contracts dict:
        data = response['http_data']['data']['contract']
        data = {data['id']:data}
        update_cache_dict(data,self.cache_path)
        return data

    #----------
    def fulfill_contract(self,contract:str) -> dict:
        """Mark a contract as done and receive payment for finishing the contract"""
        # === UNTESTED ===
        url = f"{self.base_url}/{contract}/fulfill"
        response = self.stc.stc_http_request(method="POST",url=url)
        #NOTE: Fulfilling the contract seems to transfer the 'award' credits to my agent's account
        #Upon receiving this response, I could instantly add the amount to my account (in 'agent')
        #details.

        #Transforming returned data to be compatible with contracts dict:
        data = self.mold_contract_dict(response)
        update_cache_dict(data,self.cache_path)
        return data

    #----------
    def negotiate_new_contract(self,ship:str) -> None:
        """Get offered a new contract - provided ship must be at a faction HQ waypoint"""
        url = f"{self.stc.base_url}/my/ships/{ship}/negotiate/contract"
        response = self.stc.stc_http_request(method="POST",url=url)
        if not self.stc.response_ok(response): return
        self.reload_contracts_in_cache()
