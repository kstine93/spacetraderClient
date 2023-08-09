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
def contracts_loop(ship:ShipOperator,headerFunc:Callable) -> None:
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
def choose_contract() -> None:
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
    cli_print(f"Contract {chosen_contract} accepted")

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
def request_new_contract() -> None:
    cli_print("Attempting to get new contract...")
    new_contract = ship_operator.negotiate_contract()
    if new_contract:
        cli_print("New Contract Received:")
        cli_print(format_contract_template(new_contract),contracts_menu_color)

#==========
def deliver_for_current_contract() -> None:
    '''
    TODO: This function probably needs tweaking to also check if ship is in the correct location.
    Test this once I have contracts I could deliver for!
    '''
    contract = ship_operator.get_pursuedContract()
    if len(contract) == 0:
        cli_print("No current contract selected - aborting.")
        return None
    #Note: The rest of this code currently assumes that this is a 'procurement' contract, as no
    #other types are seemingly available in the game yet. Once they are, this code must change to
    #handle these other contract types.
    deliver_details = contract['terms']['deliver']
    for item in deliver_details:
        symbol = item['tradeSymbol']
        units_req = item['unitsRequired']
        units_done = item['unitsFulfilled']

        cargo_items = [item for item in ship_operator.cargo['inventory'] if item['symbol'] == symbol]
        if not cargo_items:
            cli_print(f"No '{symbol}' units in ship cargo - cannot deliver this item.")
            break
        #At this point, we know we have >= 1 unit of item in cargo.

        units_in_cargo = cargo_items[0]['units']
        #set 'units_in_cargo' to max of what is in cargo - or whatever is needed to
        #fulfill contract (whatever is lower)
        target_quant = units_done - units_req
        if target_quant < units_in_cargo:
            data = ship_operator.deliver_pursuedContract(symbol,quantity=target_quant)
            #if we are delivering the last items of a contract, also seek to 'fulfill' contract:
            data = ship_operator.fulfill_pursuedcontract()
        else:
            data = ship_operator.deliver_pursuedContract(symbol,quantity=units_in_cargo)

#==========
contracts_menu = {
    "list all contracts": {
        "func": lambda: print_contracts_info(),
        "desc": "Print information about all available contracts."
    },
    "show current contract": {
        "func": lambda: print_current_contract_info(),
        "desc": "Print information about your current contract."
    },
    "choose current contract": {
        "func": lambda: choose_contract(),
        "desc": "Choose a contract to pursue and fulfill."
    },
    "request new contract": {
        "func": lambda: request_new_contract(),
        "desc": "Request a new contract from the faction at your current waypoint."
    },
    "deliver goods for current contract": {
        "func": lambda: deliver_for_current_contract(),
        "desc": "Deliver goods from your cargo to the target contract waypoint."
    },
    "cancel": {
        "func": lambda: None,
        "desc": "Cancel and return to previous menu."
    }
}