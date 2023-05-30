#==========
from typing import Callable
from .base import SpaceTraderConnection,DictCacheManager
from .systems import Systems

#==========
class Ships(SpaceTraderConnection,DictCacheManager):
    """
    Class to query and edit game data related to ships.
    """
    #----------
    cache_path: str | None = None 
    cache_file_name: str | None = None
    sys: Systems = Systems()

    #----------
    def __init__(self):
        SpaceTraderConnection.__init__(self)
        DictCacheManager.__init__(self)
        self.base_url = self.base_url + "/my/ships"
        #Using callsign as file name so that ship files are associated with a particular account:
        self.cache_path = f"{self.base_cache_path}ships/{self.callsign}.json"

    def mold_waypoint_list(self,http_data:dict) -> list[dict]:
        waypoint_list = http_data['data']['waypoints']
        """Index into response dict from API to get waypoint data in common format"""
        for waypoint in waypoint_list:
            del waypoint['systemSymbol']
        return waypoint_list

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
    def cache_waypoint_list(func: Callable) -> Callable:
        """
        Decorator. Uses class variables in current class and passes them to wrapper function.
        This version reads the cached ships data and tries to find information about the existing ships.
        If the file exists, but there is no data on the given ship, this information is added to the file.
        If no file exists, a file is created and the data added to it.
        """
        def wrapper(self,**kwargs):
            system_name = SpaceTraderConnection.get_system_from_waypoint(self,waypoint)
            system_data = self.sys.get_system(system_name)
            file_path = self.base_cache_path + "systems/" + system_name[0:4] + ".json"
            return DictCacheManager.custom_get_cache_dict(self,file_path,system_data,func,**kwargs)
        return wrapper

    #---------- 
    def reload_all_ships_in_cache(self,page:int=1) -> None:
        for ship_list in self.stc_get_paginated_data("GET",self.base_url,page):
            for ship in ship_list:
                transformed_ship = {ship["symbol"]:ship}
                self.update_cache_dict(transformed_ship,self.cache_path)

    #----------
    #@cache_ship
    def get_ship(self,ship:str) -> dict:
        url = self.base_url + "/" + ship
        new_response = self.stc_http_request(method="GET",url=url)
        #Transforming returned data to be compatible with ships dict:
        return {new_response["http_data"]["data"]["symbol"]:new_response["http_data"]["data"]}

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
        body = {"systemSymbol":system}
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def nav_ship_to_waypoint(self,ship:str, waypoint:str) -> None:
        url = f"{self.base_url}/{ship}/navigate"
        body = {"waypointSymbol":waypoint}
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def get_nav_details(self,ship:str) -> dict:
        url = f"{self.base_url}/{ship}/nav"
        response = self.stc_http_request(method="GET",url=url)
        return response["http_data"]["data"]

    #----------
    def warp_ship(self,ship:str,waypoint:str) -> None:
        #NOTE: It"s not entirely clear to me how this is different from Jump + nav commands.
        url = f"{self.base_url}/{ship}/warp"
        body = {"waypointSymbol":waypoint}
        self.stc_http_request(method="GET",url=url,body=body)

    #-------------
    #--SURVEYING--
    #-------------
    def chart_current_waypoint(self,ship:str) -> bool:
        #NOTE: returns non-200 code if waypoint is already charted. Maybe I only call this if I can"t find the waypoint
        #in the systems data? Should probably also be able to handle this valid non-200 response here.
        url = f"{self.base_url}/{ship}/chart"
        self.stc_http_request(method="POST",url=url)

    #----------
    #----------
    #----------
    from .custom_types import SpaceTraderResp
    def handle_standard_responses(response:SpaceTraderResp) -> dict:
        """Function for dealing with standard responses from Spacetrader API (e.g., if status == 201 and data == {x}, then do y)"""
        #If parsing fails, it"s likely because of a failed API request
        match response["http_status"]:
            case 200:
                return response["http_data"]
            case 201:
                return response["http_data"]
            case 409:
                #409 seems to be returned when we try to do something that"s not allowed in the game
                return {}


    #----------
    #----------
    #----------


    #----------
    def survey_current_waypoint(self,ship:str) -> list[dict]|None:
        #NOTE: This is a unique endpoint in that it creates a new type of data: SURVEY data.
        #Need to find way to attach this to waypoint data somehow.
        url = f"{self.base_url}/{ship}/survey"
        response = self.stc_http_request(method="POST",url=url)
        match response["http_status"]:
            case 201:
                return response["http_data"]["data"]["surveys"]
            case 409:
                print(response["http_data"]["error"]["message"])
                return None
            case _:
                msg = f"API call received unexpected status: {response['http_status']}. Message: {response['http_data']}"
                raise Exception(msg)

    #----------
    def scan_systems(self,ship:str) -> list[dict]:
        #NOTE: This is returning an array of systems. It"s not clear to me how this differs
        #from "list_systems"
        #NOTE: Can fail if ship not in orbit - need to handle this valid non-200 response.
        #This is the same case for "waypoints" and "ships".
        url = f"{self.base_url}/{ship}/scan/systems"
        self.stc_http_request(method="POST",url=url)


    def proto_scan_waypoints(self,ship:str) -> dict:
        pass

    #----------
    @cache_waypoint_list
    def scan_waypoints(self,ship:str) -> list[dict]:
        #NOTE: This appears to be very similar to "scan systems" - is it only getting info from the current system?
        url = f"{self.base_url}/{ship}/scan/waypoints"
        response = self.stc_http_request(method="POST",url=url)
        data = self.mold_waypoint_list(response["http_data"])
        return data

    #----------
    def scan_for_ships(self,ship:str) -> dict:
        #NOTE: This is unique- appears to get information on other nearby ships
        #NOTE: This needs a "cooldown" between uses - so failing to cache this data is actually problematic.
        #CACHE THIS SOMEHOW.
        #NOTE: This returns a non-200 response by default - even when the scan works.
        #This is the same for system and waypoint scans.
        url = f"{self.base_url}/{ship}/scan/ships"
        response = self.stc_http_request(method="POST",url=url)
        return response["http_data"]["data"]["ships"]

    #-------------------
    #--SHIP MANAGEMENT--
    #-------------------
    def get_cooldown_details(self,ship:str) -> None:
        #Will respond with valid non-200 response codes (204 means there is no cooldown)
        url = f"{self.base_url}/{ship}/cooldown"
        response = self.stc_http_request(method="GET",url=url)
        return response["http_data"]["data"]

    #----------
    def refuel_ship(self,ship:str) -> dict:
        url = f"{self.base_url}/{ship}/refuel"
        self.stc_http_request(method="POST",url=url)

    #----------
    def set_nav_speed(self,ship:str,speed:str) -> None:
        url = f"{self.base_url}/{ship}/nav"
        body = {"flightMode":speed}
        self.stc_http_request(method="PATCH",url=url,body=body)

    #----------
    def negotiate_contract(self,ship:str) -> dict:
        #NOTE: This appears to be an unfinished endpoint which would arguably go better in the contracts class.
        #No need to develop this until it"s clarified a bit better.
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
            "tradeSymbol":item
            ,"units":quantity
            ,"shipSymbol":target_ship
        }
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def purchase_cargo(self,ship:str,item:str,quantity:int) -> None:
        url = f"{self.base_url}/{ship}/purchase"
        body = {
            "tradeSymbol":item
            ,"units":quantity
        }
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def sell_cargo(self,ship:str,item:str,quantity:int) -> None:
        url = f"{self.base_url}/{ship}/sell"
        body = {
            "symbol":item
            ,"units":quantity
        }
        self.stc_http_request(method="POST",url=url,body=body)

    #----------
    def jettison_cargo(self,ship:str,item:str,quantity:int) -> None:
        url = f"{self.base_url}/{ship}/jettison"
        body = {
            "tradeSymbol":item
            ,"units":quantity
        }
        self.stc_http_request(method="POST",url=url,body=body)