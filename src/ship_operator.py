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
from .utilities.basic_utilities import time_diff_seconds

#==========
class ShipOperator():
    """
    Class to operate a ship
    """
    #----------
    ships = Ships()
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

    #Flight Status
    status:str
    flightMode:str
    arrivalTime:str

    #Ship Info
    shipCrew:dict
    shipFrame:dict
    shipReactor:dict
    shipModules:list[dict]
    shipMounts:list[dict]

    #Cooldown
    cooldownExpiry:str | None = None

    #Contract
    pursued_contract:str | None = None

    #----------
    def __init__(self,ship_name):
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
            seconds = self.get_cooldown_seconds()
            if seconds > 0:
                print(f"Cooldown remaining: {seconds}s")
                return None

            result = func(self,*args,**kwargs)
            cooldown_res = self.ships.get_cooldown(self.spaceship_name)
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
        agent_data = self.ships.stc.get_agent()
        self.__set_credits(agent_data)

    #----------
    def reload_ship_details(self) -> None:
        """Update local data on ship status, location, cargo, fuel and crew"""
        response = self.ships.get_ship(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
        data = response['http_data']['data']
        #setting Flight Status attributes
        self.__set_location(data['nav'])
        self.__set_flight_status(data['nav'])

        #setting Ship Info attributes
        self.__set_crew(data['crew'])
        self.__set_mounts(data['mounts'])
        self.__set_modules(data['modules'])
        self.__set_frame(data['frame'])
        self.__set_reactor(data['reactor'])

        #setting Inventory attributes
        self.__set_cargo(data['cargo'])
        self.__set_fuel(data['fuel'])

    #----------
    def reload_nav_details(self) -> None:
        response = self.ships.get_nav_details(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
        data = response['http_data']['data']

        self.__set_location(data)
        self.__set_flight_status(data)

    #----------
    def reload_cargo_details(self) -> None:
        response = self.ships.get_current_cargo(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
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
        self.shipMounts = mounts_details

    #----------
    def __set_modules(self,modules_details:dict) -> None:
        self.shipModules = modules_details

    #----------
    def __set_reactor(self,reactor_details:dict) -> None:
        self.shipReactor = reactor_details

    #----------
    def __set_frame(self,frame_details:dict) -> None:
        self.shipFrame = frame_details

    #----------
    def __set_crew(self,crew_details:dict) -> None:
        self.shipCrew = crew_details

    #----------
    def __set_fuel(self,fuel_details:dict) -> None:
        self.fuel = fuel_details

    #----------
    def __set_credits(self,agent_details:dict) -> None:
        self.credits = agent_details['credits']

    #------------------
    #--ENRICHING DATA--
    #------------------
    @check_set_cooldown
    def scan_for_ships(self) -> None:
        self.orbit()
        response = self.ships.scan_for_ships(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
        self.nearby_ships = response['http_data']['data']['ships']

    #----------
    @check_set_cooldown
    def scan_systems(self) -> None:
        self.orbit()
        response = self.ships.scan_systems(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
        self.nearby_systems = response['http_data']['data']['systems']

    #----------
    @check_set_cooldown
    def scan_waypoints(self) -> None:
        """Scan waypoints in system to get additional data. Ship action. Incurs cooldown."""
        self.orbit()
        response = self.ships.scan_waypoints(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
        #Error typically indicates ship is on cooldown:
        if response["http_status"] not in [200,201]:
            return None
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
    def survey_waypoint(self) -> None:
        self.orbit()
        response = self.ships.survey_current_waypoint(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return None
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
        response = self.ships.set_ship_speed(self.spaceship_name,speed)
        if not self.ships.stc.response_ok(response): return
        nav_data = response['http_data']['data']
        self.__set_flight_status(nav_data)

    #----------
    def orbit(self) -> None:
        response = self.ships.orbit_ship(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
        nav_data = response['http_data']['data']['nav']
        self.__set_flight_status(nav_data)

    #----------
    def dock(self) -> None:
        response = self.ships.dock_ship(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
        nav_data = response['http_data']['data']['nav']
        self.__set_flight_status(nav_data)

    #----------
    def nav(self, waypoint: str) -> None:
        self.orbit()
        response = self.ships.nav_to_waypoint(self.spaceship_name, waypoint)
        if not self.ships.stc.response_ok(response): raise Exception #If navigation fails
        self.reload_nav_details()

    #----------
    def jump(self,system:str) -> None:
        self.orbit()
        response = self.ships.jump_ship_to_system(self.spaceship_name,system)
        if not self.ships.stc.response_ok(response): return
        self.new_system_data_reset()

    #----------
    def warp(self,waypoint:str) -> None:
        self.orbit()
        response = self.ships.warp_ship(self.spaceship_name,waypoint)
        if not self.ships.stc.response_ok(response): return
        self.new_system_data_reset()

    #-------------
    #--RESOURCES--
    #-------------
    def get_cooldown_seconds(self) -> int:
        """Most ship actions invoke a cooldown period.
        See how much more time until a ship action can be taken."""
        if self.cooldownExpiry == None:
            return 0
        else:
            return time_diff_seconds(self.cooldownExpiry)

    #----------
    def get_surveys_current_waypoint(self) -> list[dict] | None:
        """Get the list of surveys that are not expired and valid at the ship's current waypoint"""
        surveys = self.surveys
        curr_wp = self.curr_waypoint['symbol']
        #Get surveys valid at current waypoint
        surveys = list(filter(lambda survey: survey['symbol'] == curr_wp, surveys))
        #Get non-expired surveys:
        surveys = list(filter(lambda survey: time_diff_seconds(survey['expiration']) > 0, surveys))
        return surveys

    #----------
    @check_set_cooldown
    def extract(self,survey:dict={}) -> None | dict:
        """Extract resources from current waypoint using optional survey"""
        self.orbit()

        response = self.ships.extract_resources(self.spaceship_name,survey)
        if not self.ships.stc.response_ok(response): return None

        self.__set_cargo(response['http_data']['data']['cargo'])
        #Returning so that we can know what new resources we gained.
        return response['http_data']['data']['extraction']['yield']

    #----------
    def extract_by_resource(self,target_resource:str) -> None | dict:
        """Extract resources from current waypoint. If a survey data structure
        exists for the current waypoint, use it. If one of the survey data structures
        matches the target_resource, use that specifically"""

        survey = self.__get_optimal_survey(target_resource)
        return self.extract(survey)

    #----------
    def __get_optimal_survey(self,target_resource:str) -> dict:
        """Get surveys valid in the current waypoint. Sorts this list based on if survey
        contains target_resource and then based on size. Returns best-choice survey."""
        if not self.get_surveys_current_waypoint():
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
    def refine(self,product:RefinableProduct) -> None | dict:
        ##UNTESTED! Requires ship with refining module.
        response = self.ships.refine_product(self.spaceship_name,product)
        if not self.ships.stc.response_ok(response): return None
        self.__set_cargo(response['http_data']['data']['cargo'])
        return response['http_data']['data']['produced']

    #----------
    def refuel(self) -> None:
        self.dock()
        response = self.ships.refuel_ship(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
        self.__set_fuel(response['http_data']['data']['fuel'])


    #---------
    #--CARGO--
    #---------
    def sell(self,item:str,quantity:int|None) -> None:
        if not quantity:
            quantity = self.get_cargo_quantity(item)
        self.dock()
        response = self.ships.sell_cargo(self.spaceship_name,item,quantity)
        if not self.ships.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])
        self.__set_credits(response['http_data']['data']['agent'])

    #----------
    def purchase(self,item:str,quantity:int) -> None:
        self.dock()
        response = self.ships.purchase_cargo(self.spaceship_name,item,quantity)
        if not self.ships.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])
        self.__set_credits(response['http_data']['data']['agent'])

    #----------
    def jettison(self,item:str,quantity:int) -> None:
        response = self.ships.jettison_cargo(self.spaceship_name,item,quantity)
        if not self.ships.stc.response_ok(response): return
        self.__set_cargo(response['http_data']['data']['cargo'])

    #----------
    def transfer_cargo(self,item:str,quantity:int,target_ship:str) -> None:
        response = self.ships.transfer_cargo_to_ship(self.spaceship_name,item,quantity,target_ship)
        if not self.ships.stc.response_ok(response): return
        self.reload_cargo_details()

    #----------
    def install_mount(self,mount: str) -> None:
        response = self.ships.install_ship_mount(self.spaceship_name, mount)
        if not self.ships.stc.response_ok(response): return
        self.reload_ship_details()

    #----------
    def remove_mount(self,mount: str) -> None:
        response = self.ships.remove_ship_mount(self.spaceship_name, mount)
        if not self.ships.stc.response_ok(response): return
        self.reload_ship_details()

    #----------
    def get_mounts(self) -> None:
        response = self.ships.get_ship_mounts(self.spaceship_name)
        if not self.ships.stc.response_ok(response): return
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

    #----------
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