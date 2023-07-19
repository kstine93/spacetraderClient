"""
Data and functions related for interacting with the 'contracts' endpoint of the Spacetrader API
"""
#==========
from .base import SpaceTraderConnection
from .utilities.custom_types import SpaceTraderResp

#==========
class Contracts:
    """
    Class to query and edit game data related to contracts.
    """
    #----------
    base_url:str
    stc = SpaceTraderConnection()

    #----------
    def __init__(self):
        self.base_url = self.stc.base_url + "/my/contracts"

    def mold_contract_dict(self,response:SpaceTraderResp) -> dict:
        '''Index into response dict from API to get contract data in common format'''
        data = response['http_data']['data']
        return {data['id']:data}

    #----------
    def list_all_contracts(self,page:int=1) -> None:
        """Force-updates all contracts data in cache with data from the API"""
        contracts = []
        for contract_list in self.stc.stc_get_paginated_data("GET",self.base_url,page):
            for con in contract_list["http_data"]["data"]:
                contracts.append({con['id']:con})
        return contracts

    #----------
    def get_contract(self,contract:str) -> dict:
        """Get information about a specific contract"""
        url = self.base_url + "/" + contract
        response = self.stc.stc_http_request(method="GET",url=url)
        if not self.stc.response_ok(response): return {}
        data = self.mold_contract_dict(response)
        return data

    #----------
    def accept_contract(self,contract:str) -> dict:
        """Accept an in-game contract from the list of available contracts"""
        url = f"{self.base_url}/{contract}/accept"
        response = self.stc.stc_http_request(method="POST",url=url)
        if not self.stc.response_ok(response): return {}
        data = response['http_data']['data']['contract']
        data = {data['id']:data}
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
        data = response['http_data']['data']['contract']
        data = {data['id']:data}
        return data

    #----------
    def fulfill_contract(self,contract:str) -> dict:
        """Mark a contract as done and receive payment for finishing the contract"""
        # === UNTESTED ===
        url = f"{self.base_url}/{contract}/fulfill"
        response = self.stc.stc_http_request(method="POST",url=url)
        if not self.stc.response_ok(response): return {}
        data = self.mold_contract_dict(response)
        return data

    #----------
    def negotiate_new_contract(self,ship:str) -> None:
        """Get offered a new contract - provided ship must be at a faction HQ waypoint"""
        url = f"{self.stc.base_url}/my/ships/{ship}/negotiate/contract"
        self.stc.stc_http_request(method="POST",url=url)
