"""
Data and functions related for interacting with the 'ships' endpoint of the Spacetrader API
"""
#==========
import json
from typing import Callable

from .agent import Agent
from .ships import Ships
from .systems import Systems
from .utilities.custom_types import RefinableProduct, NavSpeed
from .utilities.cache_utilities import update_cache_dict
from .utilities.basic_utilities import time_seconds_diff_UTC
from .art.animations import *

#==========
class ShipOperator(Ships):
    """
    Class to operate a ship
    """
    #----------
    systems = Systems()
    agent = Agent()

    #----------
    #Name
    spaceship_name:str | None = None

    #Location
    curr_system:dict | None = None
    curr_waypoint:dict | None = None

    #Enriched data
    surveys:list[dict] = []
    nearby_ships:list[dict] = []
    nearby_systems:list[dict] = []

    #Inventory
    cargo:dict | None = None
    fuel:dict | None = None
    credits:int | None = None
    mounts:list[dict] | None = None

    #Flight Status
    status:str | None = None
    flightMode:str | None = None
    arrivalTime:str | None = None

    #Crew
    crew:dict | None = None

    #Cooldown
    cooldownExpiry:str | None = None

    #----------
    def __init__(self,ship_name):
        super().__init__()
        self.spaceship_name = ship_name
        self.reload_ship_details()

    #----------
    def p(self,attr:str):
        """Alternative print for class attributes"""
        res = self.__getattribute__(attr)
        if isinstance(res,dict) or isinstance(res,list):
            print(json.dumps(res,indent=2))
        else:
            print(res)

    #----------
    def check_set_cooldown(func: Callable) -> Callable:
        """Wrapper to check cooldown before attempting an action, and to set a new cooldown afterwards"""
        def wrapper(self,*args,**kwargs):
            if self.cooldownExpiry:
                seconds = time_seconds_diff_UTC(self.cooldownExpiry)
                if seconds > 0:
                    print(f"Cooldown remaining: {seconds}s")
                    return

            result = func(self,*args,**kwargs)
            cooldown_res = self.get_cooldown(self.spaceship_name)
            if cooldown_res['http_data']:
                self.cooldownExpiry = cooldown_res['http_data']['data']['expiration']
            return result
        return wrapper

    #-------------------
    #--BASIC SHIP DATA--
    #-------------------
    def new_system_data_reset(self) -> None:
        """Upon traveling to a new system, reset local data appropriately."""
        self.reload_ship_details()
        self.reload_agent_details()
        #Reseting variables which are volatile or lose relevance in a new system:
        self.nearby_ships = []
        self.nearby_systems = []

    #----------
    def reload_agent_details(self) -> None:
        """Update local data with agent information - particularly credit balance."""
        agent_data = self.agent.get_agent(self.stc.callsign)
        self.__set_credits(agent_data[self.stc.callsign])

    #----------
    def reload_ship_details(self) -> None:
        """Update local data on ship status, location, cargo, fuel and crew"""
        response = super().get_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        data = response['http_data']['data']

        self.__set_location(data['nav'])
        self.__set_flight_status(data['nav'])
        self.__set_cargo(data['cargo'])
        self.__set_fuel(data['fuel'])
        self.__set_crew(data['crew'])
        self.__set_mounts(data['mounts'])
        self.__set_modules(data['modules'])

    #----------
    def reload_nav_details(self) -> None:
        response = super().get_nav_details(self.spaceship_name)
        if not self.stc.response_ok(response): return
        data = response['http_data']['data']

        self.__set_location(data)
        self.__set_flight_status(data)

    #----------
    def reload_cargo_details(self) -> None:
        response = super().get_cargo(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data'])

    #----------
    #TODO: make custom dict type for nav_details?
    def __set_location(self,nav_details:dict) -> None:
        """Update local data on ship's location"""
        sys_name = nav_details['systemSymbol']
        wp_name = nav_details['waypointSymbol']

        sys_data = self.systems.get_system(sys_name)
        sys_data = sys_data[sys_name]
        sys_data = self.systems.simplify_system_dict(sys_data)
        #Get single waypoint data embedded in system data in a list:
        wp_data = next((wp for wp in sys_data['waypoints'] if wp['symbol'] == wp_name),False)

        self.curr_system = sys_data
        self.curr_waypoint = wp_data

    #----------
    def __set_flight_status(self,nav_details:dict) -> None:
        self.status = nav_details['status']
        self.flightMode = nav_details['flightMode']
        self.arrivalTime = nav_details['route']['arrival']

    #----------
    def __set_cargo(self,cargo_details:dict) -> None:
        self.cargo = cargo_details

    #----------
    def __set_mounts(self,mounts_details:dict) -> None:
        self.mounts = mounts_details

    #----------
    def __set_modules(self,modules_details:dict) -> None:
        self.modules = modules_details

    #----------
    def __set_fuel(self,fuel_details:dict) -> None:
        self.fuel = fuel_details

    #----------
    def __set_crew(self,crew_details:dict) -> None:
        self.crew = crew_details

    #----------
    def __set_credits(self,agent_details:dict) -> None:
        self.credits = agent_details['credits']

    #-------------------
    #--ENCRICHING DATA--
    #-------------------
    @check_set_cooldown
    def scan_for_ships(self) -> None:
        self.orbit_ship()
        response = super().scan_for_ships(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.nearby_ships = response['http_data']['data']['ships']

    #----------
    @check_set_cooldown
    def scan_systems(self) -> None:
        self.orbit_ship()
        response = super().scan_systems(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.nearby_systems = response['http_data']['data']['systems']

    #----------
    @check_set_cooldown
    def scan_waypoints(self) -> None:
        """Scan waypoints in system to get additional data. Ship action. Incurs cooldown."""
        self.orbit_ship()
        response = super().scan_waypoints(self.spaceship_name)
        if not self.stc.response_ok(response): return
        #Error typically indicates ship is on cooldown:
        if response["http_status"] not in [200,201]:
            return response['http_data']['error']
        wp_data = response['http_data']['data']['waypoints']
        self.__enrich_waypoint_cache(wp_data)
        self.reload_nav_details()

    #----------
    def __enrich_waypoint_cache(self,waypointData:dict) -> None:
        """Enrich persistent Systems cache in file with enriched waypoints data"""
        system = waypointData[0]['systemSymbol']
        system_data = self.systems.get_system(system)

        #Updating system data
        system_data[system]['waypoints'] = waypointData
        cache_path = self.systems.create_cache_path(system)
        update_cache_dict(system_data,cache_path)

    #----------
    @check_set_cooldown
    def survey_waypoint(self) -> dict:
        response = super().survey_current_waypoint(self.spaceship_name)
        if not self.stc.response_ok(response): return
        data = response['http_data']['data']
        self.surveys = self.surveys + data['surveys']

    #--------------
    #--NAVIGATION--
    #--------------
    def set_speed(self,speed:NavSpeed) -> None:
        response = super().set_speed(self.spaceship_name,speed)
        if not self.stc.response_ok(response): return
        nav_data = response['http_data']['data']
        self.__set_flight_status(nav_data)

    #----------
    def orbit_ship(self) -> dict:
        response = super().orbit_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        nav_data = response['http_data']['data']['nav']
        self.__set_flight_status(nav_data)

    #----------
    def dock_ship(self) -> None:
        response = super().dock_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        nav_data = response['http_data']['data']['nav']
        self.__set_flight_status(nav_data)

    #----------
    def nav_to_waypoint(self, waypoint: str) -> None:
        self.orbit_ship()
        response = super().nav_ship_to_waypoint(self.spaceship_name, waypoint)
        if not self.stc.response_ok(response): return
        #Animating + showing travel time
        arrival_time_str = response['http_data']['data']['nav']['route']['arrival']
        seconds_to_arrival = time_seconds_diff_UTC(arrival_time_str)
        animate_navigation(seconds_to_arrival)

        self.reload_nav_details()

    #----------
    def jump_ship_to_system(self,system:str) -> None:
        response = super().jump_ship_to_system(self.spaceship_name,system)
        if not self.stc.response_ok(response): return
        self.new_system_data_reset()
        print(f" === Jump complete. Arrived at {system} ===")

    #----------
    def warp_ship(self,waypoint:str) -> None:
        response = super().warp_ship(self.spaceship_name,waypoint)
        if not self.stc.response_ok(response): return
        #Animating + showing travel time
        arrival_time_str = response['http_data']['data']['nav']['route']['arrival']
        seconds_to_arrival = time_seconds_diff_UTC(arrival_time_str)
        animate_navigation(seconds_to_arrival)

        self.new_system_data_reset()
        print(f" === Warp complete. Arrived at {waypoint} ===")

    #-------------
    #--RESOURCES--
    #-------------
    @check_set_cooldown
    def extract_resources(self,target_resource:str) -> None:
        """Extract resources from current waypoint. If a survey data structure
        exists for the current waypoint, use it. If one of the survey data structures
        matches the target_resource, use that specifically"""
        survey = self.__get_optimal_survey(target_resource)
        response = super().extract_resources(self.spaceship_name,survey)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])

    #----------
    def __get_optimal_survey(self,target_resource:str) -> dict:
        """Get surveys valid in the current waypoint. Sorts this list based on if survey
        contains target_resource and then based on size. Returns best-choice survey."""
        if not self.surveys:
            return {} #"Blank" survey if we have no surveys
        wp_symbol = self.curr_waypoint['symbol']
        #Get surveys for current waypoint
        wp_surveys = list(filter(lambda item: item['symbol'] == wp_symbol,self.surveys))
        #Sort surveys based on target resource & then size
        def rsc_condition(survey):
            return target_resource in [deposit['symbol'] for deposit in survey['deposits']]
        def size_condition(survey):
            return {"SMALL":1,"MODERATE":2,"LARGE":3}[survey['size']]
        wp_surveys.sort(key=lambda x: (-rsc_condition(x), -size_condition(x)))
        return wp_surveys[0]

    #----------
    @check_set_cooldown
    def refine_product(self,product:RefinableProduct) -> None:
        ##UNTESTED! Requires ship with refining module.
        response = super().refine_product(self.spaceship_name,product)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])

    #----------
    def refuel_ship(self) -> None:
        self.dock_ship()
        response = super().refuel_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.__set_fuel(response['http_data']['data']['fuel'])


    #---------
    #--CARGO--
    #---------
    def sell_cargo(self,item:str,quantity:int) -> None:
        self.dock_ship()
        response = super().sell_cargo(self.spaceship_name,item,quantity)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])
        self.__set_credits(response['http_data']['data']['agent'])

    #----------
    def purchase_cargo(self,item:str,quantity:int) -> None:
        self.dock_ship()
        response = super().purchase_cargo(self.spaceship_name,item,quantity)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])
        self.__set_credits(response['http_data']['data']['agent'])

    #----------
    def jettison_cargo(self,item:str,quantity:int) -> None:
        response = super().jettison_cargo(self.spaceship_name,item,quantity)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])

    #----------
    def transfer_cargo_to_ship(self,item:str,quantity:int,target_ship:str) -> None:
        response = super().transfer_cargo_to_ship(self.spaceship_name,item,quantity,target_ship)
        if not self.stc.response_ok(response): return
        self.reload_cargo_details()

    #----------
    def install_mount(self,mount: str) -> None:
        response = super().install_mount(self.spaceship_name, mount)
        if not self.stc.response_ok(response): return
        self.reload_ship_details()

    #----------
    def remove_mount(self,mount: str) -> None:
        response = super().remove_mount(self.spaceship_name, mount)
        if not self.stc.response_ok(response): return
        self.reload_ship_details()

    #----------
    def get_mounts(self) -> None:
        response = super().get_mounts(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.__set_mounts(response['http_data']['data'])