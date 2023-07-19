from copy import deepcopy
from typing import Callable
from cli_utilities import cli_print, cli_clear, use_game_menu
from src.contracts import Contracts
from src.ship_operator import ShipOperator
from art.str_formatting import (format_contract_list,
                                format_contract_template
)

#==========
ship_operator:ShipOperator

#==========
contracts_menu_color = "chartreuse2" #Color used by default in cli_print

#==========
def contracts_loop(ship:ShipOperator,headerFunc:Callable) -> bool:
    """Allows printing information about, and interacting with, contract information
    As opposed to other loops in other menus, this menu is not intended to be lingered on - it is
    instead intended to emulate the previous menu that players were on. For that reason, the
    provided 'headerFunc' shows the same header as the previous menu and as soon as players make a
    selection from the menu below, they are returned to that previous menu.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    headerFunc()
    use_game_menu(contracts_menu)

    return False

#==========
def print_contracts_info() -> None:
    """Print information about player contracts"""
    contracts = Contracts()
    data = contracts.list_all_contracts()
    if len(data) > 0:
        cli_print(format_contract_list(data),color=contracts_menu_color)
    else:
        cli_print("(No contracts yet negotiated)",color=contracts_menu_color)

#==========
def print_current_contract_info() -> None:
    """Print information about player contracts"""
    data = ship_operator.check_contract()
    if data:
        cli_print(format_contract_template(data),color=contracts_menu_color)
    else:
        cli_print("(No contracts yet negotiated)",color=contracts_menu_color)


#==========
contracts_menu = {
    "list all contracts": {
        "func": lambda: print_current_contract_info(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "show current contract": {
        "func": lambda: print_current_contract_info(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "switch current contract": {
        "func": lambda: print_current_contract_info(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "request new contract": {
        "func": lambda: print_current_contract_info(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "accept a contract": {
        "func": lambda: print_current_contract_info(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "deliver goods for current contract": {
        "func": lambda: print_current_contract_info(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "cancel": {
        "func": lambda: None,
        "desc": "Don't show any information and return to previous menu."
    }
}