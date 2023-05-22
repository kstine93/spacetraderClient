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
        self.cache_path = self.base_cache_path + "contracts/"
        #Using callsign as convenient name for files related to current user:
        self.cache_file_name = self.callsign

    #----------
    def cache_contracts(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached contracts data and tries to find information about the existing contracts.
        If no cache file exists, one is created.
        """
        def wrapper(self,**kwargs):
            new_path = self.cache_path + self.cache_file_name + ".json"
            return DictCacheManager.read_cache_file(self,new_path,func,**kwargs)
        return wrapper
    
    #----------
    def update_contracts(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached contracts data and tries to find information about the given contract.
        If the file exists, but there is no data on the given contract, this information is added to the file.
        If no file exists, a warning is given but NO FILE IS CREATED.
        """
        def wrapper(self,contract,**kwargs):
            new_path = self.cache_path + self.cache_file_name + ".json"
            return DictCacheManager.update_cache_dict(self,new_path,contract,func,**kwargs)
        return wrapper
    
    #---------- 
    def force_update_contracts(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version does not attempt to return any matching cached records. Instead, it 
        just updates the record.
        Since a force update might contain unique information that can't
        be queried again, it cannot afford to fail because the records file did not exist.
        For that reason, this function calls the 'list_contracts' function again to just ensure that
        the file has been created.
        """
        def wrapper(self,contract,**kwargs):
            path = self.cache_path + self.cache_file_name + ".json"
            return DictCacheManager.update_cache_dict(self,path,contract,func,force=True,**kwargs)
        return wrapper

    #----------
    @cache_contracts
    def list_contracts(self) -> dict:
        #TODO: This API call is paginated. Adapt this method to iterate through pages until all data is collected.
        #TODO: Decide how often I want to update this information...How long before I don't trust that I'm not missing
        # new contract data?
        data = self.stc_http_request(method="GET",url=self.base_url)
        #Transforming nested list to dict to make data easier to reference:
        return {obj['id']:obj for obj in data['data']}
    
    #----------
    @update_contracts
    def get_contract(self,contract:str) -> dict:
        url = self.base_url + "/" + contract
        new_data = self.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with contracts dict:
        return {contract:new_data['data']}

    #----------
    @force_update_contracts
    def accept_contract(self,contract:str) -> dict:
        url = f"{self.base_url}/{contract}/accept"
        new_data = self.stc_http_request(method="POST",url=url)
        #Transforming returned data to be compatible with contracts dict:
        return {contract:new_data['data']['contract']}

    #----------
    @force_update_contracts
    def deliver_contract(self,contract:str) -> dict:
        # === UNTESTED ===
        url = f"{self.base_url}/{contract}/deliver"
        new_data = self.stc_http_request(method="POST",url=url)
        #NOTE: This method also returns a 'cargo' object which represents the type and quantity
        #of resource which was delivered. I could pass this object to my 'fleet' class to update
        #the quantity of the resource for the ship which was delivering this contract.

        #Transforming returned data to be compatible with contracts dict:
        return {contract:new_data['data']['contract']}

    #----------
    @force_update_contracts
    def fulfill_contract(self,contract:str) -> dict:
        # === UNTESTED ===
        url = f"{self.base_url}/{contract}/fulfill"
        new_data = self.stc_http_request(method="POST",url=url)
        #NOTE: Fulfilling the contract seems to transfer the 'award' credits to my agent's account
        #Upon receiving this response, I could instantly add the amount to my account balance (in 'agent')
        #details.

        #Transforming returned data to be compatible with contracts dict:
        return {contract:new_data['data']['contract']}