"""
Data and functions related for interacting with the 'ships' endpoint of the Spacetrader API
"""
#==========
import json
from typing import Callable

from .ships import Ships
from .markets import Markets
from .systems import Systems
from .contracts import Contracts
from .utilities.custom_types import RefinableProduct, NavSpeed, MarginObj
from .utilities.cache_utilities import update_cache_dict
from .utilities.basic_utilities import time_seconds_diff_UTC

#==========
class ShipOperator(Ships):
    """
    Class to operate a ship
    """
    #----------
    systems = Systems()
    markets = Markets()
    contracts = Contracts()

    #----------
    #Name
    spaceship_name:str

    #Location
    curr_system:dict
    curr_waypoint:dict

    #Enriched data
    surveys:list[dict] = []
    nearby_ships:list[dict] = []
    nearby_systems:list[dict] = []

    #Inventory
    cargo:dict
    fuel:dict
    credits:int
    mounts:list[dict]

    #Flight Status
    status:str
    flightMode:str
    arrivalTime:str

    #Crew
    crew:dict

    #Cooldown
    cooldownExpiry:str

    #Contract
    pursued_contract:str | None = None

    #----------
    def __init__(self,ship_name):
        super().__init__()
        self.spaceship_name = ship_name
        self.reload_ship_details()
        self.reload_agent_details()

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
        self.reload_nav_details()
        #Reseting variables which are volatile or lose relevance in a new system:
        self.nearby_ships = []
        self.nearby_systems = []

    #----------
    def reload_agent_details(self) -> None:
        """Update local data with agent information - particularly credit balance."""
        agent_data = self.stc.get_agent(self.stc.callsign)
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
        response = super().get_current_cargo(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data'])

    #----------
    #TODO: make custom dict type for nav_details?
    def __set_location(self,nav_details:dict) -> None:
        """Update local data on ship's location"""
        sys_name = nav_details['systemSymbol']
        wp_name = nav_details['waypointSymbol']

        sys_data = self.systems.get_system(sys_name)
        sys_data = sys_data[sys_name] #TODO: This fails when jumping to new system - test
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
    def __set_mounts(self,mounts_details:list[dict]) -> None:
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

    #------------------
    #--ENRICHING DATA--
    #------------------
    @check_set_cooldown
    def scan_for_ships(self) -> None:
        self.orbit()
        response = super().scan_for_ships(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.nearby_ships = response['http_data']['data']['ships']

    #----------
    @check_set_cooldown
    def scan_systems(self) -> None:
        self.orbit()
        response = super().scan_systems(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.nearby_systems = response['http_data']['data']['systems']

    #----------
    @check_set_cooldown
    def scan_waypoints(self) -> None:
        """Scan waypoints in system to get additional data. Ship action. Incurs cooldown."""
        self.orbit()
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
        cache_path = self.systems.__create_cache_path(system)
        update_cache_dict(system_data,cache_path)

    #----------
    @check_set_cooldown
    def survey_waypoint(self) -> None:
        self.orbit()
        response = super().survey_current_waypoint(self.spaceship_name)
        if not self.stc.response_ok(response): return None
        data = response['http_data']['data']
        self.surveys = self.surveys + data['surveys']

    #----------
    def get_market(self,waypoint:str|None = None) -> dict:
        """Wrapper for get_market, since whether we rely on the cache or not
        depends on ship location"""
        if not waypoint:
            waypoint = self.curr_waypoint['symbol']
        if waypoint == self.curr_waypoint['symbol']:
            return self.markets.update_market(waypoint)
        else:
            return self.markets.get_market(waypoint)

    #----------
    def find_best_margins(self,limit:int=3) -> list[MarginObj]:
        return self.markets.find_best_margins(limit)

    #----------
    def find_margin(self,item:str) -> MarginObj:
        return self.markets.find_margin(item)

    #--------------
    #--NAVIGATION--
    #--------------
    def set_speed(self,speed:NavSpeed) -> None:
        response = super().set_ship_speed(self.spaceship_name,speed)
        if not self.stc.response_ok(response): return
        nav_data = response['http_data']['data']
        self.__set_flight_status(nav_data)

    #----------
    def orbit(self) -> None:
        response = super().orbit_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        nav_data = response['http_data']['data']['nav']
        self.__set_flight_status(nav_data)

    #----------
    def dock(self) -> None:
        response = super().dock_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        nav_data = response['http_data']['data']['nav']
        self.__set_flight_status(nav_data)

    #----------
    def nav(self, waypoint: str) -> None:
        self.orbit()
        response = super().nav_to_waypoint(self.spaceship_name, waypoint)
        if not self.stc.response_ok(response): return
        self.reload_nav_details()

    #----------
    def jump(self,system:str) -> None:
        self.orbit()
        response = super().jump_ship_to_system(self.spaceship_name,system)
        if not self.stc.response_ok(response): return
        self.new_system_data_reset()

    #----------
    def warp(self,waypoint:str) -> None:
        self.orbit()
        response = super().warp_ship(self.spaceship_name,waypoint)
        if not self.stc.response_ok(response): return
        self.new_system_data_reset()

    #-------------
    #--RESOURCES--
    #-------------
    @check_set_cooldown
    def extract(self,target_resource:str) -> None:
        """Extract resources from current waypoint. If a survey data structure
        exists for the current waypoint, use it. If one of the survey data structures
        matches the target_resource, use that specifically"""
        self.orbit()
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
    def refine(self,product:RefinableProduct) -> None:
        ##UNTESTED! Requires ship with refining module.
        response = super().refine_product(self.spaceship_name,product)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])

    #----------
    def refuel(self) -> None:
        self.dock()
        response = super().refuel_ship(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.__set_fuel(response['http_data']['data']['fuel'])


    #---------
    #--CARGO--
    #---------
    def sell(self,item:str,quantity:int|None) -> None:
        if not quantity:
            quantity = self.get_cargo_quantity(item)
        self.dock()
        response = super().sell_cargo(self.spaceship_name,item,quantity)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])
        self.__set_credits(response['http_data']['data']['agent'])

    #----------
    def purchase(self,item:str,quantity:int) -> None:
        self.dock()
        response = super().purchase_cargo(self.spaceship_name,item,quantity)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])
        self.__set_credits(response['http_data']['data']['agent'])

    #----------
    def jettison(self,item:str,quantity:int) -> None:
        response = super().jettison_cargo(self.spaceship_name,item,quantity)
        if not self.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])

    #----------
    def transfer_cargo(self,item:str,quantity:int,target_ship:str) -> None:
        response = super().transfer_cargo_to_ship(self.spaceship_name,item,quantity,target_ship)
        if not self.stc.response_ok(response): return
        self.reload_cargo_details()

    #----------
    def install_mount(self,mount: str) -> None:
        response = super().install_ship_mount(self.spaceship_name, mount)
        if not self.stc.response_ok(response): return
        self.reload_ship_details()

    #----------
    def remove_mount(self,mount: str) -> None:
        response = super().remove_ship_mount(self.spaceship_name, mount)
        if not self.stc.response_ok(response): return
        self.reload_ship_details()

    #----------
    def get_mounts(self) -> None:
        response = super().get_ship_mounts(self.spaceship_name)
        if not self.stc.response_ok(response): return
        self.__set_mounts(response['http_data']['data'])

    #----------
    def get_cargo_quantity(self,item:str) -> int:
        """Return quantity of item in cargo"""
        inventory = self.cargo['inventory']
        for cargo in inventory:
            if cargo['symbol'] == item:
                return cargo['units']
        return 0

    #-------------
    #--CONTRACTS--
    #-------------
    def list_contracts(self) -> dict:
        return self.contracts.list_all_contracts()

    def __pick_first_contract(self) -> str:
        """Returns first contract in list_contracts. Ensures contract methods always reference a
        contract without requiring user to provide it every time."""
        cons = self.list_contracts()
        return list(cons.keys())[0]

    #----------
    def accept_contract(self,contract:str|None=pursued_contract) -> None:
        """Wrapper to negotiate new contract (requires ship to be at a faction HQ)"""
        if not contract:
            contract = self.__pick_first_contract()
        self.contracts.accept_contract(contract)
    #----------
    def check_contract(self,contract:str|None=pursued_contract) -> dict:
        """Return currently-pursued contract data - so player doesn't need contract ID always"""
        if not contract:
            contract = self.__pick_first_contract()
        self.pursued_contract = contract
        return self.contracts.get_contract(contract)

    #----------
    def deliver_contract(self,item:str,quantity:int|None=None,contract:str|None=pursued_contract) -> None:
        """Attempt to deliver item for currently-pursued contract"""
        self.dock()
        if not contract:
            contract = self.__pick_first_contract()
        if not quantity:
            quantity = self.get_cargo_quantity(item)
        self.contracts.deliver_contract(contract,self.spaceship_name,item,quantity)

    #----------
    def fulfill_contract(self,contract:str|None=pursued_contract) -> None:
        if not contract:
            contract = self.__pick_first_contract()
        self.contracts.fulfill_contract(contract)
        self.reload_agent_details() #Reloading credits

    #----------
    def negotiate_contract(self) -> None:
        """Wrapper to negotiate new contract (requires ship to be at a faction HQ)"""
        self.dock()
        self.contracts.negotiate_new_contract(self.spaceship_name)