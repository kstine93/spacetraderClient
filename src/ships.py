"""
Data and functions related for interacting with the 'ships' endpoint of the Spacetrader API
"""
#==========
from .base import SpaceTraderConnection
from .utilities.custom_types import RefinableProduct, SpaceTraderResp, NavSpeed
from .utilities.cache_utilities import update_cache_dict,attempt_dict_retrieval

#==========
class Ships:
    """
    Class to query and edit game data related to ships.
    """
    #----------
    stc = SpaceTraderConnection()
    cache_path: str
    cache_file_name: str

    #----------
    def __init__(self):
        self.base_url = self.stc.base_url + "/my/ships"
        #Using callsign as file name so that ship files are associated with a particular account:
        self.cache_path = f"{self.stc.base_cache_path}ships/{self.stc.callsign}.json"

    #----------
    def get_ship(self,ship:str) -> SpaceTraderResp:
        """Get detailed information about the ship, its systems, cargo, crew and modules"""
        url = self.base_url + "/" + ship
        return self.stc.stc_http_request(method="GET",url=url)

    #----------
    def reload_ships_in_cache(self,page:int=1) -> None:
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
    def orbit_ship(self,ship:str) -> SpaceTraderResp:
        """orbit the ship at the current waypoint"""
        url = f"{self.base_url}/{ship}/orbit"
        return self.stc.stc_http_request(method="POST",url=url)

    #----------
    def dock_ship(self,ship:str) -> SpaceTraderResp:
        """dock the ship at the current waypoint"""
        url = f"{self.base_url}/{ship}/dock"
        return self.stc.stc_http_request(method="POST",url=url)

    #----------
    def jump_ship_to_system(self,ship:str, system:str) -> SpaceTraderResp:
        """Jump instantaneously to another system. Alternative to warp."""
        url = f"{self.base_url}/{ship}/jump"
        body = {'systemSymbol':system}
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #----------
    def nav_to_waypoint(self,ship:str, waypoint:str) -> SpaceTraderResp:
        """Navigate the ship to a given waypoint"""
        url = f"{self.base_url}/{ship}/navigate"
        body = {"waypointSymbol":waypoint}
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #----------
    def get_nav_details(self,ship:str) -> SpaceTraderResp:
        """Get current navigation details for a ship"""
        url = f"{self.base_url}/{ship}/nav"
        return self.stc.stc_http_request(method="GET",url=url)

    #----------
    def warp_ship(self,ship:str,waypoint:str) -> SpaceTraderResp:
        """Navigate (warp) the ship to a different system without jumping"""
        url = f"{self.base_url}/{ship}/warp"
        body = {'waypointSymbol':waypoint}
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #-------------
    #--SURVEYING--
    #-------------
    def chart_current_waypoint(self,ship:str) -> SpaceTraderResp:
        """Add the current waypoint to the community-wide directory of waypoints,
        if the record doesn't already exist."""
        url = f"{self.base_url}/{ship}/chart"
        return self.stc.stc_http_request(method="POST",url=url)

    #----------
    def survey_current_waypoint(self,ship:str) -> SpaceTraderResp:
        """Get a survey of resources at your current waypoint location"""
        url = f"{self.base_url}/{ship}/survey"
        return self.stc.stc_http_request(method="POST",url=url)

    #----------
    def scan_systems(self,ship:str) -> SpaceTraderResp:
        """Get information about systems close to the current system"""
        url = f"{self.base_url}/{ship}/scan/systems"
        return self.stc.stc_http_request(method="POST",url=url)

    #----------
    def scan_waypoints(self,ship:str) -> SpaceTraderResp:
        """Get detailed data on waypoints in the current system
        NOTE: This updates the cache with the new data as well."""
        url = f"{self.base_url}/{ship}/scan/waypoints"
        return self.stc.stc_http_request(method="POST",url=url)

    #----------
    def scan_for_ships(self,ship:str) -> SpaceTraderResp:
        """Look for ships in the current system"""
        url = f"{self.base_url}/{ship}/scan/ships"
        return self.stc.stc_http_request(method="POST",url=url)

    #-------------------
    #--SHIP MANAGEMENT--
    #-------------------
    def get_cooldown(self,ship:str) -> SpaceTraderResp:
        """Most ship actions invoke a cooldown period.
        See how much more time until a ship action can be taken."""
        url = f"{self.base_url}/{ship}/cooldown"
        return self.stc.stc_http_request(method="GET",url=url)

    #----------
    def refuel_ship(self,ship:str) -> SpaceTraderResp:
        """Add fuel to ship. Requires that refueling is possible in current location."""
        url = f"{self.base_url}/{ship}/refuel"
        return self.stc.stc_http_request(method="POST",url=url)

    #----------
    def set_ship_speed(self,ship:str,speed:NavSpeed) -> SpaceTraderResp:
        """Set navigation speed for the ship."""
        url = f"{self.base_url}/{ship}/nav"
        body = {'flightMode':speed}
        return self.stc.stc_http_request(method="PATCH",url=url,json=body)

    #----------
    def extract_resources(self,ship:str,survey_dict:dict={}) -> SpaceTraderResp:
        """Extract resources from the current waypoint. an optional survey object allows better yields."""
        url = f"{self.base_url}/{ship}/extract"
        return self.stc.stc_http_request(method="POST",url=url, json=survey_dict)

    #----------
    def refine_product(self,ship:str,product:RefinableProduct) -> SpaceTraderResp:
        """Attempt to refine raw materials on the ship into target product"""
        url = f"{self.base_url}/{ship}/refine"
        body = {'produce':product}
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #----------
    def get_ship_mounts(self,ship:str) -> SpaceTraderResp:
        """Get mounts currently installed on ship"""
        url = f"{self.base_url}/{ship}/mounts"
        return self.stc.stc_http_request(method="POST",url=url)

    #----------
    def install_ship_mount(self,ship:str,mount:str) -> SpaceTraderResp:
        """Install mount in Cargo onto ship"""
        url = f"{self.base_url}/{ship}/mounts/install"
        body = {'symbol':mount}
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #----------
    def remove_ship_mount(self,ship:str,mount:str) -> SpaceTraderResp:
        """Remove mount in Cargo onto ship"""
        url = f"{self.base_url}/{ship}/mounts/remove"
        body = {'symbol':mount}
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #---------
    #--CARGO--
    #---------
    def get_current_cargo(self,ship:str) -> SpaceTraderResp:
        """See current cargo of a ship"""
        url = f"{self.base_url}/{ship}/cargo"
        return self.stc.stc_http_request(method="GET",url=url)

    #----------
    def transfer_cargo_to_ship(self,ship:str,item:str,quantity:int,target_ship:str) -> SpaceTraderResp:
        """Move cargo in-between two ships at the same waypoint"""
        url = f"{self.base_url}/{ship}/transfer"
        body = {
            'tradeSymbol':item
            ,'units':quantity
            ,'shipSymbol':target_ship
        }
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #----------
    def purchase_cargo(self,ship:str,item:str,quantity:int) -> SpaceTraderResp:
        """buy cargo at the waypoint the ship is currently at"""
        url = f"{self.base_url}/{ship}/purchase"
        body = {
            'symbol':item
            ,'units':quantity
        }
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #----------
    def sell_cargo(self,ship:str,item:str,quantity:int) -> SpaceTraderResp:
        """Sell cargo at the waypoint the ship is currently at"""
        url = f"{self.base_url}/{ship}/sell"
        body = {
            'symbol':item
            ,'units':quantity
        }
        return self.stc.stc_http_request(method="POST",url=url,json=body)

    #----------
    def jettison_cargo(self,ship:str,item:str,quantity:int) -> SpaceTraderResp:
        """Remove cargo from the storage of a ship"""
        url = f"{self.base_url}/{ship}/jettison"
        body = {
            'symbol':item
            ,'units':quantity
        }
        return self.stc.stc_http_request(method="POST",url=url,json=body)