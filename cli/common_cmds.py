from copy import deepcopy
from cli_utilities import cli_print
from src.contracts import Contracts
from src.ship_operator import ShipOperator
from art.str_formatting import (format_contract_list,
                                format_ship_info_template,
                                format_cargo_info_template,
                                format_ship_mount_info_template)

#=========
#== HUD ==
#=========
def print_ship_info(ship_operator:ShipOperator,color:str="white"):
    """Print out HUD relevant to mining on the CLI"""
    string = format_ship_info_template(ship_operator.spaceship_name,
                              deepcopy(ship_operator.curr_waypoint),
                              ship_operator.credits
                              )
    cli_print(string,color)

#=========
def print_cargo_info(ship_operator:ShipOperator,color:str="white"):
    """Print information about ship cargo using stateful information in provided ShipOperator"""
    string = format_cargo_info_template(deepcopy(ship_operator.cargo))
    cli_print(string,color)

#=========
def print_ship_mount_info(ship_operator:ShipOperator,color:str="white"):
    """Print information about ship mounts using stateful information in provided ShipOperator"""
    string = format_ship_mount_info_template(deepcopy(ship_operator.shipMounts))
    cli_print(string,color)

#==========
def print_contracts_info(color:str="chartreuse2") -> None:
    """Print information about player contracts"""
    contracts = Contracts()
    data = contracts.list_all_contracts()
    cli_print(format_contract_list(data),color)