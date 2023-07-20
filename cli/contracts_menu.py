from copy import deepcopy
from typing import Callable
from cli_utilities import *
from src.contracts import Contracts
from src.ship_operator import ShipOperator
from art.str_formatting import (format_contract_list,
                                format_contract_template
)

#==========
ship_operator:ShipOperator
contracts = Contracts()

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
    data = contracts.list_all_contracts()
    if len(data) > 0:
        cli_print(format_contract_list(data),color=contracts_menu_color)
    else:
        cli_print("(No contracts yet negotiated)",color=contracts_menu_color)

#==========
def print_current_contract_info() -> None:
    """Print information about player contracts"""
    data = ship_operator.get_pursuedContract()
    if data:
        cli_print(format_contract_template(data),color=contracts_menu_color)
    else:
        cli_print("(No contracts yet negotiated)",color=contracts_menu_color)

#==========
def choose_contract():
    contract_list = contracts.list_all_contracts()
    chosen_contract = pick_contract_from_menu(contract_list)

    #If contract already accepted:
    contract = [con for con in contract_list if con['id'] == chosen_contract]
    if contract[0]['accepted'] == True:
        ship_operator.set_pursuedContractId(chosen_contract)
        return

    accept = "Yes, accept this contract."
    decline = "No, do not accept."
    menu = create_menu(menu_items=[accept,decline],prompt="Accept this contract? Unfinished contracts can damage your reputation!")
    resp = menu_prompt(menu)

    if resp == decline:
        return

    ship_operator.accept_contract(chosen_contract)
    ship_operator.set_pursuedContractId(chosen_contract)

#==========
def pick_contract_from_menu(contract_list:list[dict]) -> str:
    menu_items = []
    for item in contract_list:
        preview = format_contract_template(item)
        preview = preview.replace("|","\|") #For preview in menu, normal bars must be escaped.
        menu_items.append(f"{item['id']}|{preview}")

    contract_menu = create_menu(menu_items,
                                "Pick the contract you would like to pursue:",
                                preview_command=lambda x: x, #print traits to preview box
                                preview_title="Contract description",
                                preview_size=0.5)
    return menu_prompt(contract_menu)

#==========
def request_new_contract():
    cli_print("Attempting to get new contract...")
    new_contract = ship_operator.negotiate_contract()
    if new_contract:
        cli_print("New Contract Received:")
        cli_print(format_contract_template(new_contract),contracts_menu_color)

#==========
def deliver_for_current_contract():
    '''
    Functionality:
    1. Get pursuedContract details.
    2. Get item(s) that need to be procured from contract details
        2a. NOTE: This could be just 1 item (it is now), but it could in the future be multiple...
        2b. NOTE: I don't have any examples of contracts that are NOT acquiring and delivering items,
            but in the future, this could happen...
    3. Get 'quantity' of item from cargo
    4. If quantity more than 0, call 'deliver' function
    5. Check if total delivered amount exceeds contract requirements
        5a. If yes, call 'fulfill contract'
    '''
    pass

#==========
contracts_menu = {
    "list all contracts": {
        "func": lambda: print_contracts_info(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "show current contract": {
        "func": lambda: print_current_contract_info(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "choose current contract": {
        "func": lambda: choose_contract(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "request new contract": {
        "func": lambda: request_new_contract(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "deliver goods for current contract": {
        "func": lambda: deliver_for_current_contract(),
        "desc": "Print information about your current ship's cargo and crew."
    },
    "cancel": {
        "func": lambda: None,
        "desc": "Don't show any information and return to previous menu."
    }
}