"""
Data and functions related for interacting with the 'ships' endpoint of the Spacetrader API
"""
#==========
from .ships import Ships
from .systems import Systems
from .utilities.cache_utilities import update_cache_dict

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

    #----------
    def __init__(self,ship_name):
        super().__init__()
        self.spaceship_name = ship_name

    #-------------------
    #--BASIC SHIP DATA--
    #-------------------
    def reload_entire_ship(self) -> None:
        """Update local data on ship status, location, cargo, fuel and crew"""
        response = self.get_ship(self.spaceship_name)
        data = response['http_data']['data']

        self.__set_location(data['nav'])
        self.__set_flight_status(data['nav'])
        self.__set_cargo(data['cargo'])
        self.__set_fuel(data['fuel'])
        self.__set_crew(data['crew'])

    #----------
    def reload_nav_details(self) -> None:
        response = self.get_nav_details(self.spaceship_name)
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
        self.current_status = cargo_details

    #----------
    def __set_fuel(self,fuel_details:dict) -> None:
        """Update local data on ship's fuel"""
        self.current_status = fuel_details

    #----------
    def __set_crew(self,crew_details:dict) -> None:
        """Update local data on ship's fuel"""
        self.current_status = crew_details

    #-------------------
    #--ENCRICHING DATA--
    #-------------------
    def enrich_current_waypoints(self) -> None:
        """Scan waypoints in system to get additional data. Ship action. Incurs cooldown."""
        response = self.scan_waypoints(self.spaceship_name)
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
    def survey_current_waypoint(self) -> dict:
        data = super().survey_current_waypoint(self.spaceship_name)
        self.current_surveys = self.current_surveys + data['http_data']['data']['surveys']