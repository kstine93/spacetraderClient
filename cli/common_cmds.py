from copy import deepcopy
from cli_utilities import cli_print
from src.contracts import Contracts
from src.ships import Ships
from src.ship_operator import ShipOperator
from art.str_formatting import (format_base_hud_template,
                                format_contract_list,
                                format_general_info_template,
                                format_frame_info_template,
                                format_reactor_info_template,
                                format_engine_info_template,
                                format_cargo_info_template,
                                format_crew_info_template,
                                format_ship_mount_info_template,
                                format_ship_modules_info_template
)

#=========
#== HUD ==
#=========
def print_hud(ship_operator:ShipOperator) -> str:
    flightMode = deepcopy(ship_operator.flightMode)
    fuel = deepcopy(ship_operator.fuel)
    system = deepcopy(ship_operator.curr_system)
    credits = deepcopy(ship_operator.credits)
    waypoint = deepcopy(ship_operator.curr_waypoint)
    hud = format_base_hud_template(flightMode,system,waypoint,fuel,credits)
    cli_print(hud)

#=========
def print_ship_info(ship_operator:ShipOperator,color:str="white"):
    string = format_frame_info_template(deepcopy(ship_operator.shipFrame))
    string += format_reactor_info_template(deepcopy(ship_operator.shipReactor))
    string += format_engine_info_template(deepcopy(ship_operator.shipEngine))
    cli_print(string,color)

#=========
def print_cargo_info(ship_operator:ShipOperator,color:str="white"):
    """Print information about ship cargo using stateful information in provided ShipOperator"""
    string = format_cargo_info_template(deepcopy(ship_operator.cargo))
    cli_print(string,color)

#=========
def print_crew_info(ship_operator:ShipOperator,color:str="white"):
    """Print information about ship cargo using stateful information in provided ShipOperator"""
    string = format_crew_info_template(deepcopy(ship_operator.shipCrew))
    cli_print(string,color)

#=========
def print_ship_mount_info(ship_operator:ShipOperator,color:str="white"):
    """Print information about ship mounts using stateful information in provided ShipOperator"""
    mountPoints = ship_operator.shipFrame['mountingPoints']
    string = format_ship_mount_info_template(deepcopy(ship_operator.shipMounts),mountPoints)
    cli_print(string,color)

#=========
def print_ship_module_info(ship_operator:ShipOperator,color:str="white"):
    """Print information about ship mounts using stateful information in provided ShipOperator"""
    moduletSlots = ship_operator.shipFrame['moduleSlots']
    string = format_ship_modules_info_template(deepcopy(ship_operator.shipMounts),moduletSlots)
    cli_print(string,color)

#==========
def print_contracts_info(color:str="chartreuse2") -> None:
    """Print information about player contracts"""
    contracts = Contracts()
    data = contracts.list_all_contracts()
    cli_print(format_contract_list(data),color)