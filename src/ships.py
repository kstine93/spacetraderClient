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
    def get_ship(self,ship:str) -> dict:
        """Get detailed information about the ship, its systems, cargo, crew and modules"""
        url = self.base_url + "/" + ship
        response = self.stc_http_request(method="GET",url=url)
        return response

    #--------------
    #--NAVIGATION--
    #--------------
    def orbit_ship(self,ship:str) -> dict:
        """orbit the ship at the current waypoint"""
        url = f"{self.base_url}/{ship}/orbit"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #----------
    def dock_ship(self,ship:str) -> dict:
        """dock the ship at the current waypoint"""
        url = f"{self.base_url}/{ship}/dock"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #----------
    def jump_ship_to_system(self,ship:str, system:str) -> dict:
        """Jump instantaneously to another system. Alternative to warp."""
        url = f"{self.base_url}/{ship}/jump"
        body = {'systemSymbol':system}
        response = self.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def nav_ship_to_waypoint(self,ship:str, waypoint:str) -> dict:
        """Navigate the ship to a given waypoint"""
        url = f"{self.base_url}/{ship}/navigate"
        body = {'waypointSymbol':waypoint}
        response = self.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def get_nav_details(self,ship:str) -> dict:
        """Get current navigation details for a ship"""
        url = f"{self.base_url}/{ship}/nav"
        response = self.stc_http_request(method="GET",url=url)
        return response

    #----------
    def warp_ship(self,ship:str,waypoint:str) -> None:
        """Navigate (warp) the ship to a different system without jumping"""
        url = f"{self.base_url}/{ship}/warp"
        body = {'waypointSymbol':waypoint}
        response = self.stc_http_request(method="GET",url=url,body=body)
        return response

    #-------------
    #--SURVEYING--
    #-------------
    def chart_current_waypoint(self,ship:str) -> dict:
        """Add the current waypoint to the community-wide directory of waypoints, if the record doesn't already exist."""
        url = f"{self.base_url}/{ship}/chart"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #----------
    def survey_current_waypoint(self,ship:str) -> dict:
        """Get a survey of resources at your current waypoint location"""
        url = f"{self.base_url}/{ship}/survey"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #----------
    def scan_systems(self,ship:str) -> dict:
        """Get information about systems close to the current system"""
        url = f"{self.base_url}/{ship}/scan/systems"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #----------
    def scan_waypoints(self,ship:str) -> dict:
        """Get detailed data on waypoints in the current system"""
        url = f"{self.base_url}/{ship}/scan/waypoints"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #----------
    def scan_for_ships(self,ship:str) -> dict:
        url = f"{self.base_url}/{ship}/scan/ships"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #-------------------
    #--SHIP MANAGEMENT--
    #-------------------
    def get_cooldown_details(self,ship:str) -> dict:
        """Most ship actions invoke a cooldown period.
        See how much more time until a ship action can be taken."""
        url = f"{self.base_url}/{ship}/cooldown"
        response = self.stc_http_request(method="GET",url=url)
        return response

    #----------
    def refuel_ship(self,ship:str) -> dict:
        url = f"{self.base_url}/{ship}/refuel"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #----------
    def set_nav_speed(self,ship:str,speed:str) -> dict:
        """Set navigation speed for the ship."""
        url = f"{self.base_url}/{ship}/nav"
        body = {'flightMode':speed}
        response = self.stc_http_request(method="PATCH",url=url,body=body)
        return response

    #----------
    def negotiate_contract(self,ship:str) -> dict:
        #NOTE: This appears to be an unfinished endpoint which would arguably go better in the contracts class.
        #No need to develop this until it's clarified a bit better.
        pass

    #----------
    def extract_resources(self,ship:str,surveyDict:dict={}) -> dict:
        """Extract resources from the current waypoint. an optional survey object allows better yields."""
        url = f"{self.base_url}/{ship}/extract"
        response = self.stc_http_request(method="POST",url=url,body=surveyDict)
        return response

    #----------
    def refine_material(self,ship:str,material:str) -> dict:
        url = f"{self.base_url}/{ship}/refine"
        response = self.stc_http_request(method="POST",url=url)
        return response

    #---------
    #--CARGO--
    #---------
    def get_current_cargo(self,ship:str) -> dict:
        """See current cargo of a ship"""
        url = f"{self.base_url}/{ship}/cargo"
        response = self.stc_http_request(method="GET",url=url)
        return response

    #----------
    def transfer_cargo_to_ship(self,ship:str,item:str,quantity:int,target_ship:str) -> dict:
        """Move cargo in-between two ships at the same waypoint"""
        url = f"{self.base_url}/{ship}/transfer"
        body = {
            'tradeSymbol':item
            ,'units':quantity
            ,'shipSymbol':target_ship
        }
        response = self.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def purchase_cargo(self,ship:str,item:str,quantity:int) -> dict:
        """buy cargo at the waypoint the ship is currently at"""
        url = f"{self.base_url}/{ship}/purchase"
        body = {
            'tradeSymbol':item
            ,'units':quantity
        }
        response = self.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def sell_cargo(self,ship:str,item:str,quantity:int) -> dict:
        """Sell cargo at the waypoint the ship is currently at"""
        url = f"{self.base_url}/{ship}/sell"
        body = {
            'symbol':item
            ,'units':quantity
        }
        response = self.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def jettison_cargo(self,ship:str,item:str,quantity:int) -> dict:
        """Remove cargo from the storage of a ship"""
        url = f"{self.base_url}/{ship}/jettison"
        body = {
            'tradeSymbol':item
            ,'units':quantity
        }
        response = self.stc_http_request(method="POST",url=url,body=body)
        return response