"""
Data and functions related for interacting with the 'ships' endpoint of the Spacetrader API
"""
#==========
from .base import SpaceTraderConnection
from .utilities.cache_utilities import update_cache_dict,attempt_dict_retrieval

#==========
class Ships:
    """
    Class to query and edit game data related to ships.
    """
    #----------
    stc = SpaceTraderConnection()
    cache_path: str | None = None
    cache_file_name: str | None = None

    #----------
    def __init__(self):
        self.base_url = self.stc.base_url + "/my/ships"
        #Using callsign as file name so that ship files are associated with a particular account:
        self.cache_path = f"{self.stc.base_cache_path}ships/{self.stc.callsign}.json"

    #----------
    def get_ship(self,ship:str) -> dict:
        """Get detailed information about the ship, its systems, cargo, crew and modules"""
        url = self.base_url + "/" + ship
        response = self.stc.stc_http_request(method="GET",url=url)
        return response

    #----------
    def list_ships(self,ship:str) -> dict:
        """Get detailed information about the ship, its systems, cargo, crew and modules"""
        url = self.base_url + "/" + ship
        response = self.stc.stc_http_request(method="GET",url=url)
        return response

    #----------
    def reload_ships_in_cache(self,page:int=1) -> dict:
        """Force-updates all ships data in cache with data from the API"""
        for ship_list in self.stc.stc_get_paginated_data("GET",self.base_url,page):
            for ship in ship_list["http_data"]["data"]:
                transformed_con = {ship['symbol']:ship}
                update_cache_dict(transformed_con,self.cache_path)

    #----------
    #TODO: Make this function below prettier.
    def list_all_ships(self) -> dict:
        """Get all ships associated with the agent"""
        data = attempt_dict_retrieval(self.cache_path)
        if not data:
            self.reload_ships_in_cache()
            #If no data is returned a 2nd time, it means no data is avaiable.
            data = attempt_dict_retrieval(self.cache_path)
        return data

    #--------------
    #--NAVIGATION--
    #--------------
    def orbit_ship(self,ship:str) -> dict:
        """orbit the ship at the current waypoint"""
        url = f"{self.base_url}/{ship}/orbit"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #----------
    def dock_ship(self,ship:str) -> dict:
        """dock the ship at the current waypoint"""
        url = f"{self.base_url}/{ship}/dock"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #----------
    def jump_ship_to_system(self,ship:str, system:str) -> dict:
        """Jump instantaneously to another system. Alternative to warp."""
        url = f"{self.base_url}/{ship}/jump"
        body = {'systemSymbol':system}
        response = self.stc.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def nav_ship_to_waypoint(self,ship:str, waypoint:str) -> dict:
        """Navigate the ship to a given waypoint"""
        url = f"{self.base_url}/{ship}/navigate"
        body = {"waypointSymbol":waypoint}
        response = self.stc.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def get_nav_details(self,ship:str) -> dict:
        """Get current navigation details for a ship"""
        url = f"{self.base_url}/{ship}/nav"
        response = self.stc.stc_http_request(method="GET",url=url)
        return response

    #----------
    def warp_ship(self,ship:str,waypoint:str) -> None:
        """Navigate (warp) the ship to a different system without jumping"""
        url = f"{self.base_url}/{ship}/warp"
        body = {'waypointSymbol':waypoint}
        response = self.stc.stc_http_request(method="GET",url=url,body=body)
        return response

    #-------------
    #--SURVEYING--
    #-------------
    def chart_current_waypoint(self,ship:str) -> dict:
        """Add the current waypoint to the community-wide directory of waypoints,
        if the record doesn't already exist."""
        url = f"{self.base_url}/{ship}/chart"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #----------
    def survey_current_waypoint(self,ship:str) -> dict:
        """Get a survey of resources at your current waypoint location"""
        url = f"{self.base_url}/{ship}/survey"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #----------
    def scan_systems(self,ship:str) -> dict:
        """Get information about systems close to the current system"""
        url = f"{self.base_url}/{ship}/scan/systems"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #----------
    def scan_waypoints(self,ship:str) -> dict:
        """Get detailed data on waypoints in the current system
        NOTE: This updates the cache with the new data as well."""
        url = f"{self.base_url}/{ship}/scan/waypoints"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #----------
    def scan_for_ships(self,ship:str) -> dict:
        """Look for ships in the current system"""
        url = f"{self.base_url}/{ship}/scan/ships"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #-------------------
    #--SHIP MANAGEMENT--
    #-------------------
    def get_cooldown_details(self,ship:str) -> dict:
        """Most ship actions invoke a cooldown period.
        See how much more time until a ship action can be taken."""
        url = f"{self.base_url}/{ship}/cooldown"
        response = self.stc.stc_http_request(method="GET",url=url)
        return response

    #----------
    def refuel_ship(self,ship:str) -> dict:
        """Add fuel to ship. Requires that refueling is possible in current location."""
        url = f"{self.base_url}/{ship}/refuel"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #----------
    def set_nav_speed(self,ship:str,speed:str) -> dict:
        """Set navigation speed for the ship."""
        url = f"{self.base_url}/{ship}/nav"
        body = {'flightMode':speed}
        response = self.stc.stc_http_request(method="PATCH",url=url,body=body)
        return response

    #----------
    def negotiate_ship(self,ship:str) -> dict:
        #NOTE: This appears to be an unfinished endpoint which would arguably
        # go better in the ships class.
        #No need to develop this until it's clarified a bit better.
        pass

    #----------
    def extract_resources(self,ship:str,survey_dict:dict={}) -> dict:
        """Extract resources from the current waypoint. an optional survey object allows better yields."""
        url = f"{self.base_url}/{ship}/extract"
        response = self.stc.stc_http_request(method="POST",url=url,body=survey_dict)
        return response

    #----------
    def refine_material(self,ship:str,) -> dict:
        """Attempt to refine any raw materials on the ship"""
        url = f"{self.base_url}/{ship}/refine"
        response = self.stc.stc_http_request(method="POST",url=url)
        return response

    #---------
    #--CARGO--
    #---------
    def get_current_cargo(self,ship:str) -> dict:
        """See current cargo of a ship"""
        url = f"{self.base_url}/{ship}/cargo"
        response = self.stc.stc_http_request(method="GET",url=url)
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
        response = self.stc.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def purchase_cargo(self,ship:str,item:str,quantity:int) -> dict:
        """buy cargo at the waypoint the ship is currently at"""
        url = f"{self.base_url}/{ship}/purchase"
        body = {
            'tradeSymbol':item
            ,'units':quantity
        }
        response = self.stc.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def sell_cargo(self,ship:str,item:str,quantity:int) -> dict:
        """Sell cargo at the waypoint the ship is currently at"""
        url = f"{self.base_url}/{ship}/sell"
        body = {
            'symbol':item
            ,'units':quantity
        }
        response = self.stc.stc_http_request(method="POST",url=url,body=body)
        return response

    #----------
    def jettison_cargo(self,ship:str,item:str,quantity:int) -> dict:
        """Remove cargo from the storage of a ship"""
        url = f"{self.base_url}/{ship}/jettison"
        body = {
            'tradeSymbol':item
            ,'units':quantity
        }
        response = self.stc.stc_http_request(method="POST",url=url,body=body)
        return response