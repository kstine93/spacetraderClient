from copy import deepcopy
from typing import Callable
from cli_utilities import cli_print, cli_clear, use_game_menu
from src.contracts import Contracts
from src.ship_operator import ShipOperator
from art.str_formatting import (format_base_hud_template,
                                format_contract_list,
                                format_frame_info_template,
                                format_reactor_info_template,
                                format_engine_info_template,
                                format_cargo_info_template,
                                format_crew_info_template,
                                format_ship_mount_info_template,
                                format_ship_modules_info_template
)

#==========
ship_operator:ShipOperator

#==========
info_menu_color = "medium_purple2" #Color used by default in cli_print

#==========
def info_loop(ship:ShipOperator,headerFunc:Callable) -> bool:
    """Displays information menu for printing info on ship systems.
    As opposed to other loops in other menus, this menu is not intended to be lingered on - it is
    instead intended to emulate the previous menu that players were on. For that reason, the
    provided 'headerFunc' shows the same header as the previous menu and as soon as players make a
    selection from the menu below, they are returned to that previous menu.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    headerFunc()
    use_game_menu(info_menu)

    return False

#=========
#== HUD ==
#=========
def print_hud(ship_operator:ShipOperator) -> str:
    shipName = deepcopy(ship_operator.spaceship_name)
    flightMode = deepcopy(ship_operator.flightMode)
    fuel = deepcopy(ship_operator.fuel)
    system = deepcopy(ship_operator.curr_system)
    credits = deepcopy(ship_operator.credits)
    waypoint = deepcopy(ship_operator.curr_waypoint)
    hud = format_base_hud_template(shipName,flightMode,system,waypoint,fuel,credits)
    cli_print(hud)

#=========
def print_ship_info():
    string = format_frame_info_template(deepcopy(ship_operator.shipFrame))
    string += format_reactor_info_template(deepcopy(ship_operator.shipReactor))
    string += format_engine_info_template(deepcopy(ship_operator.shipEngine))
    cli_print(string,color="white")

#=========
def print_cargo_info():
    """Print information about ship cargo using stateful information in provided ShipOperator"""
    string = format_cargo_info_template(deepcopy(ship_operator.cargo))
    cli_print(string,"white")

#=========
def print_crew_info():
    """Print information about ship cargo using stateful information in provided ShipOperator"""
    string = format_crew_info_template(deepcopy(ship_operator.shipCrew))
    cli_print(string,color="white")

#=========
def print_ship_mount_info():
    """Print information about ship mounts using stateful information in provided ShipOperator"""
    mountPoints = ship_operator.shipFrame['mountingPoints']
    string = format_ship_mount_info_template(deepcopy(ship_operator.shipMounts),mountPoints)
    cli_print(string,color="white")

#=========
def print_ship_module_info():
    """Print information about ship mounts using stateful information in provided ShipOperator"""
    moduleSlots = ship_operator.shipFrame['moduleSlots']
    string = format_ship_modules_info_template(deepcopy(ship_operator.shipModules),moduleSlots)
    cli_print(string,color="white")

#==========
def print_contracts_info() -> None:
    """Print information about player contracts"""
    contracts = Contracts()
    data = contracts.list_all_contracts()
    cli_print(format_contract_list(data),color="chartreuse2")

#==========
def print_cargo_and_crew() -> None:
    print_crew_info()
    print_cargo_info()

#==========
def print_all() -> None:
    print_cargo_and_crew()
    print_ship_info()
    print_ship_mount_info()
    print_ship_module_info()

#==========
info_menu = {
    "show ship cargo and crew": {
        "func": lambda: print_cargo_and_crew(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "show ship mounts": {
        "func": lambda: print_ship_mount_info(),
        "desc": "Show information about ship mounts, which allow interaction with the ship's environment, such as extracting resources."
    },
    "show ship modules": {
        "func": lambda: print_ship_module_info(),
        "desc": "Show information about ship internal modules, such as warp drives and cargo holds."
    },
    "show ship subsystems": {
        "func": lambda: print_ship_info(),
        "desc": "Show information on the ship's frame, its engine, and its power reactor."
    },
    "show all ship information": {
        "func": lambda: print_all(),
        "desc": "Show all available information about the ship."
    },
    "cancel": {
        "func": lambda: None,
        "desc": "Don't show any information and return to previous menu."
    },
}