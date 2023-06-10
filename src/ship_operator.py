"""
Data and functions related for interacting with the 'ships' endpoint of the Spacetrader API
"""
#==========
import logging
from threading import Timer
from typing import Callable
from .ships import Ships
from .systems import Systems
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

    #----------
    #Name
    spaceship_name:str | None = None

    #Location
    current_system:dict | None = None
    current_waypoint:dict | None = None

    #Enriched data
    current_surveys:list[dict] = []

    #Inventory
    current_cargo:dict | None = None
    current_fuel:dict | None = None

    #Flight Status
    current_status:str | None = None
    current_flightMode:str | None = None
    current_arrivalTime:str | None = None

    #Crew
    current_crew:dict | None = None

    #Cooldown
    cooldown_expiry:str | None = None

    #----------
    def __init__(self,ship_name):
        super().__init__()
        self.spaceship_name = ship_name

    #----------
    def check_set_cooldown(func: Callable) -> Callable:
        """Wrapper to check cooldown before attempting an action, and to set a new cooldown afterwards"""
        def wrapper(self,*args,**kwargs):
            if self.cooldown_expiry:
                seconds = time_seconds_diff_UTC(self.cooldown_expiry)
                if seconds > 0:
                    print(f"Cooldown remaining: {seconds}s")
                    return

            result = func(self,*args,**kwargs)
            cooldown_res = self.get_cooldown(self.spaceship_name)
            if cooldown_res['http_data']:
                self.cooldown_expiry = cooldown_res['http_data']['data']['expiration']
            return result
        return wrapper

    #-------------------
    #--BASIC SHIP DATA--
    #-------------------
    def reload_entire_ship(self) -> None:
        """Update local data on ship status, location, cargo, fuel and crew"""
        response = super().get_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        data = response['http_data']['data']

        self.__set_location(data['nav'])
        self.__set_flight_status(data['nav'])
        self.__set_cargo(data['cargo'])
        self.__set_fuel(data['fuel'])
        self.__set_crew(data['crew'])

    #----------
    @check_set_cooldown
    def reload_nav_details(self) -> None:
        response = super().get_nav_details(self.spaceship_name)
        if not self.stc.response_ok(response): return
        data = response['http_data']['data']

        self.__set_location(data)
        self.__set_flight_status(data)

    #----------
    #TODO: make custom dict type for nav_details?
    def __set_location(self,nav_details:dict) -> None:
        """Update local data on ship's location"""
        sys_name = nav_details['systemSymbol']
        wp_name = nav_details['waypointSymbol']

        sys_data = self.systems.get_system(sys_name)
        sys_data = sys_data[sys_name]
        #Get single waypoint data embedded in system data in a list:
        wp_data = next((wp for wp in sys_data['waypoints'] if wp['symbol'] == wp_name),False)

        self.current_system = sys_data
        self.current_waypoint = wp_data

    #----------
    def __set_flight_status(self,nav_details:dict) -> None:
        """Update local data on ship's status"""
        self.current_status = nav_details['status']
        self.current_flightMode = nav_details['flightMode']
        self.current_arrivalTime = nav_details['route']['arrival']

    #----------
    def __set_cargo(self,cargo_details:dict) -> None:
        """Update local data on ship's cargo"""
        self.current_cargo = cargo_details

    #----------
    def __set_fuel(self,fuel_details:dict) -> None:
        """Update local data on ship's fuel"""
        self.current_fuel = fuel_details

    #----------
    def __set_crew(self,crew_details:dict) -> None:
        """Update local data on ship's fuel"""
        self.current_crew = crew_details

    #-------------------
    #--ENCRICHING DATA--
    #-------------------
    def enrich_current_waypoints(self) -> None:
        """Scan waypoints in system to get additional data. Ship action. Incurs cooldown."""
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
        system_data = self.sys.get_system(system)

        #Updating system data
        system_data[system]['waypoints'] = waypointData
        cache_path = self.sys.create_cache_path(system)
        update_cache_dict(system_data,cache_path)

    #----------
    @check_set_cooldown
    def survey_current_waypoint(self) -> dict:
        response = super().survey_current_waypoint(self.spaceship_name)
        if not self.stc.response_ok(response): return
        data = response['http_data']['data']
        self.current_surveys = self.current_surveys + data['surveys']

    #--------------
    #--NAVIGATION--
    #--------------
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
    def nav_ship_to_waypoint(self, waypoint: str) -> None:
        response = super().nav_ship_to_waypoint(self.spaceship_name, waypoint)
        if not self.stc.response_ok(response): return
        #Animating + showing travel time
        arrival_time_str = response['http_data']['data']['nav']['route']['arrival']
        seconds_to_arrival = time_seconds_diff_UTC(arrival_time_str)
        animate_navigation(seconds_to_arrival)

        self.reload_nav_details()

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
        if not self.current_surveys:
            return {} #"Blank" survey if we have no surveys
        wp_symbol = self.current_waypoint['symbol']
        #Get surveys for current waypoint
        wp_surveys = list(filter(lambda item: item['symbol'] == wp_symbol,self.current_surveys))
        #Sort surveys based on target resource & then size
        def rsc_condition(survey):
            return target_resource in [deposit['symbol'] for deposit in survey['deposits']]
        def size_condition(survey):
            return {"SMALL":1,"MODERATE":2,"LARGE":3}[survey['size']]
        wp_surveys.sort(key=lambda x: (-rsc_condition(x), -size_condition(x)))
        return wp_surveys[0]

    #----------
    def refuel_ship(self) -> None:
        self.dock_ship()
        response = super().refuel_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.__set_fuel(response['http_data']['data']['fuel'])


    #----------------
    #--SHIP SYSTEMS--
    #----------------




    """
    Not yet implemented:
    jump_ship_to_system
    set_nav_speed

    scan_systems
    scan_waypoints
    scan_ships

    refine_material

    transfer_cargo_to_ship
    purchase_cargo
    sell_cargo
    jettison_cargo
    """