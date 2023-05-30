#==========
from typing import Callable
from .base import SpaceTraderConnection,DictCacheManager

#==========
class Contracts(SpaceTraderConnection,DictCacheManager):
    """
    Class to query and edit game data related to contracts.
    """
    #----------
    cache_path: str | None = None 
    cache_file_name: str | None = None

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)
        DictCacheManager.__init__(self)
        self.base_url = self.base_url + "/my/contracts"
        #Using callsign as file name so that contract files are associated with a particular account:
        self.cache_path = f"{self.base_cache_path}contracts/{self.callsign}.json"

    def mold_contract_dict(self,response:dict) -> dict:
        '''Index into response dict from API to get contract data in common format'''
        data = response['data']['contract']
        return {data['id']:data}

    #----------
    def cache_contracts(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached contracts data and tries to find information about the existing contracts.
        If the file exists, but there is no data on the given contract, this information is added to the file.
        If no file exists, a file is created and the data added to it.
        """
        def wrapper(self,contract:str,**kwargs):
            return self.get_cache_dict(self.cache_path,func,new_key=contract,**kwargs)
        return wrapper

    #---------- 
    def reload_contracts_in_cache(self,page:int=1) -> dict:
        for contract_list in self.stc_get_paginated_data("GET",self.base_url,page):
            for con in contract_list:
                transformed_con = {con['id']:con}
                self.update_cache_dict(transformed_con,self.cache_path)
            
    #---------- 
    def list_all_contracts(self) -> dict:
        return self.get_dict_from_file(self.cache_path)

    #----------
    @cache_contracts
    def get_contract(self,contract:str) -> dict:
        url = self.base_url + "/" + contract
        response = self.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with contracts dict:
        data = response['http_data']
        return {data['data']['id']:data['data']}

    #----------
    def accept_contract(self,contract:str) -> dict:
        url = f"{self.base_url}/{contract}/accept"
        response = self.stc_http_request(method="POST",url=url)
        #Transforming returned data to be compatible with contracts dict:
        new_data = self.mold_contract_dict(response)
        self.update_cache_dict(new_data,self.cache_path)

    #----------
    def deliver_contract(self,contract:str,ship:str,item:str,quantity:int) -> dict:
        url = f"{self.base_url}/{contract}/deliver"
        body = {
            'shipSymbol':ship
            ,'tradeSymbol':item
            ,'units':quantity
        }
        response = self.stc_http_request(method="POST",url=url,body=body)
        #NOTE: This method also returns a 'cargo' object which represents the type and quantity
        #of resource which was delivered. I could pass this object to my 'fleet' class to update
        #the quantity of the resource for the ship which was delivering this contract.

        #Transforming returned data to be compatible with contracts dict:
        new_data = self.mold_contract_dict(response)
        self.update_cache_dict(new_data,self.cache_path)

    #----------
    def fulfill_contract(self,contract:str) -> dict:
        # === UNTESTED ===
        url = f"{self.base_url}/{contract}/fulfill"
        response = self.stc_http_request(method="POST",url=url)
        #NOTE: Fulfilling the contract seems to transfer the 'award' credits to my agent's account
        #Upon receiving this response, I could instantly add the amount to my account balance (in 'agent')
        #details.

        #Transforming returned data to be compatible with contracts dict:
        new_data = self.mold_contract_dict(response)
        self.update_cache_dict(new_data,self.cache_path)