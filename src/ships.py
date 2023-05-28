#==========
from typing import Callable
from .base import SpaceTraderConnection,DictCacheManager

#==========
class Ships(SpaceTraderConnection,DictCacheManager):
    """
    Class to query and edit game data related to ships.
    """
    #----------
    cache_path: str | None = None 
    cache_file_name: str | None = None

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)
        DictCacheManager.__init__(self)
        self.base_url = self.base_url + "/my/ships"
        #Using callsign as file name so that ship files are associated with a particular account:
        self.cache_path = f"{self.base_cache_path}ships/{self.callsign}.json"

    #----------
    def mold_ship_dict(response:dict) -> dict:
        '''Index into response dict from API to get ship data in common format'''
        data = response['data']['ship']
        return {data['id']:data}

    #----------
    def cache_ship(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached ships data and tries to find information about the existing ships.
        If the file exists, but there is no data on the given ship, this information is added to the file.
        If no file exists, a file is created and the data added to it.
        """
        def wrapper(self,ship:str,**kwargs):
            return DictCacheManager.get_cache_dict(self,self.cache_path,func,new_key=ship,**kwargs)
        return wrapper

    #---------- 
    def reload_all_ships_in_cache(self,page:int=1) -> None:
        for ship_list in self.stc_get_paginated_data("GET",self.base_url,page):
            for ship in ship_list:
                transformed_ship = {ship['symbol']:ship}
                self.update_cache_dict(transformed_ship,self.cache_path)

    #----------
    #@cache_ship
    def get_ship(self,ship:str) -> dict:
        url = self.base_url + "/" + ship
        new_data = self.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with ships dict:
        return {new_data['data']['symbol']:new_data['data']}

    #--------------
    #--NAVIGATION--
    #--------------
    def orbit_ship(self,ship:str) -> None:
        url = f"{self.base_url}/{ship}/orbit"
        self.stc_http_request(method="POST",url=url)

    #----------
    def dock_ship(self,ship:str) -> bool:
        #NOTE: Docking can fail if the ship is not in the right location or capable of docking.
        #Prepare for valid non-200 responses.
        url = f"{self.base_url}/{ship}/dock"
        self.stc_http_request(method="POST",url=url)

    #----------
    def jump_ship_to_system(self,ship:str, system:str) -> None:
        url = f"{self.base_url}/{ship}/jump"
        body = {'systemSymbol':system}
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def nav_ship_to_waypoint(self,ship:str, waypoint:str) -> None:
        url = f"{self.base_url}/{ship}/navigate"
        body = {'waypointSymbol':waypoint}
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def get_nav_details(self,ship:str) -> dict:
        url = f"{self.base_url}/{ship}/nav"
        data = self.stc_http_request(method="GET",url=url)
        return data['data']

    #----------
    def warp_ship(self,ship:str,waypoint:str) -> None:
        #NOTE: It's not entirely clear to me how this is different from Jump + nav commands.
        url = f"{self.base_url}/{ship}/warp"
        body = {'waypointSymbol':waypoint}
        self.stc_http_request(method="GET",url=url,body=body)

    #-------------
    #--SURVEYING--
    #-------------
    def chart_current_waypoint(self,ship:str) -> bool:
        #NOTE: returns non-200 code if waypoint is already charted. Maybe I only call this if I can't find the waypoint
        #in the systems data? Should probably also be able to handle this valid non-200 response here.
        url = f"{self.base_url}/{ship}/chart"
        self.stc_http_request(method="POST",url=url)

    #----------
    def survey_current_waypoint(self,ship:str) -> list[dict]:
        #NOTE: This is a unique endpoint in that it creates a new type of data: SURVEY data.
        #Need to find way to attach this to waypoint data somehow.
        url = f"{self.base_url}/{ship}/survey"
        data = self.stc_http_request(method="POST",url=url)
        return data['data']['surveys']

    #----------
    def scan_systems(self,ship:str) -> list[dict]:
        #NOTE: This is returning an array of systems. It's not clear to me how this differs
        #from 'list_systems'
        #NOTE: Can fail if ship not in orbit - need to handle this valid non-200 response.
        #This is the same case for 'waypoints' and 'ships'.
        url = f"{self.base_url}/{ship}/scan/systems"
        self.stc_http_request(method="POST",url=url)

    #----------
    def scan_waypoints(self,ship:str) -> list[dict]:
        #NOTE: This appears to be very similar to 'scan systems' - is it only getting info from the current system?
        url = f"{self.base_url}/{ship}/scan/waypoints"
        self.stc_http_request(method="POST",url=url)

    #----------
    def scan_for_ships(self,ship:str) -> dict:
        #NOTE: This is unique- appears to get information on other nearby ships
        #NOTE: This needs a 'cooldown' between uses - so failing to cache this data is actually problematic.
        #CACHE THIS SOMEHOW.
        #NOTE: This returns a non-200 response by default - even when the scan works.
        #This is the same for system and waypoint scans.
        url = f"{self.base_url}/{ship}/scan/ships"
        data = self.stc_http_request(method="POST",url=url)
        return data['data']['ships']

    #-------------------
    #--SHIP MANAGEMENT--
    #-------------------
    def get_cooldown_details(self,ship:str) -> None:
        #Will respond with valid non-200 response codes (204 means there is no cooldown)
        url = f"{self.base_url}/{ship}/cooldown"
        data = self.stc_http_request(method="GET",url=url)
        return data['data']

    #----------
    def refuel_ship(self,ship:str) -> dict:
        url = f"{self.base_url}/{ship}/refuel"
        self.stc_http_request(method="POST",url=url)

    #----------
    def set_nav_speed(self,ship:str,speed:str) -> None:
        url = f"{self.base_url}/{ship}/nav"
        body = {'flightMode':speed}
        self.stc_http_request(method="PATCH",url=url,body=body)

    #----------
    def negotiate_contract(self,ship:str) -> dict:
        #NOTE: This appears to be an unfinished endpoint which would arguably go better in the contracts class.
        #No need to develop this until it's clarified a bit better.
        pass

    #----------
    def extract_resources(self,ship:str,surveyDict:dict={}) -> dict:
        #NOTE: Optional survey dict allows for targeting certain resources for extraction. See API docs.
        url = f"{self.base_url}/{ship}/extract"
        self.stc_http_request(method="POST",url=url,body=surveyDict)

    #----------
    def refine_material(self,ship:str,material:str) -> None:
        url = f"{self.base_url}/{ship}/refine"
        self.stc_http_request(method="POST",url=url)

    #---------
    #--CARGO--
    #---------
    def get_current_cargo(self,ship:str) -> dict:
        url = f"{self.base_url}/{ship}/cargo"
        return self.stc_http_request(method="GET",url=url)

    #----------
    def transfer_cargo_to_ship(self,ship:str,item:str,quantity:int,target_ship:str) -> None:
        url = f"{self.base_url}/{ship}/transfer"
        body = {
            'tradeSymbol':item
            ,'units':quantity
            ,'shipSymbol':target_ship
        }
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def purchase_cargo(self,ship:str,item:str,quantity:int) -> None:
        url = f"{self.base_url}/{ship}/purchase"
        body = {
            'tradeSymbol':item
            ,'units':quantity
        }
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def sell_cargo(self,ship:str,item:str,quantity:int) -> None:
        url = f"{self.base_url}/{ship}/sell"
        body = {
            'symbol':item
            ,'units':quantity
        }
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def jettison_cargo(self,ship:str,item:str,quantity:int) -> None:
        url = f"{self.base_url}/{ship}/jettison"
        body = {
            'tradeSymbol':item
            ,'units':quantity
        }
        self.stc_http_request(method="POST",url=url,body=body)