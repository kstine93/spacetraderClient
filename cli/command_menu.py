"""Holder of most commands for CLI"""
from src.ship_operator import *
from typing import Callable
from src.ships import Ships
from cli_utilities import *
from cli.info_menu import print_hud
from cli.contracts_menu import contracts_loop
from command.navigate_menu import navigate_loop
from command.mine_menu import mine_loop

#==========
ship_operator:ShipOperator

#==========
cmd_menu_color = "deep_pink4"

#==========
def print_cmd_menu_header() -> str:
    print_hud(ship_operator)
    cli_print(border_cmd_menu,cmd_menu_color)

#==========
def pick_ship(cancel_option:str) -> str:
    ships = Ships()
    data = ships.list_all_ships()
    ship_list = list(data.keys())
    ship_list.append(cancel_option)
    if len(ship_list) > 1:
        ship_menu = create_menu(ship_list,prompt="Choose a ship to command, Captain:")
        chosen_ship = menu_prompt(ship_menu)
    else:
        chosen_ship = ship_list[0]
    return chosen_ship

#==========
def ship_command_loop(returnHeaderFunc:Callable) -> CliCommand | None:
    cancel_option = "[cancel and return to main menu]"
    ship = pick_ship(cancel_option)
    if ship == cancel_option:
        return False

    cli_clear()
    cli_print("Loading ship details...",cmd_menu_color)

    global ship_operator
    ship_operator = ShipOperator(ship)

    cli_print(f"Welcome aboard {ship}, Captain")
    print_cmd_menu_header()

    prompt = "Type a command. Type 'menu' to see a list of commands."
    res = command_loop(command_menu,prompt,loop_func=print_cmd_menu_header)
    if res == "exit":
        return res

    cli_clear()
    cli_print("Returning to main menu...")
    returnHeaderFunc()
    return None

#==========
command_menu = {
    "navigate": {
        "func": lambda: navigate_loop(ship_operator,print_cmd_menu_header),
        "desc": "Navigate your ship to a new location."
    },
    "trade": {
        "func": lambda: trade_menu(ship_operator),
        "desc": "Purchase, sell and study profitable markets"
    },
    "explore": {
        "func": lambda: explore_menu(ship_operator),
        "desc": "Learn more about surrounding ships, waypoints and systems."
    },
    "mine": {
        "func": lambda: mine_loop(ship_operator,print_cmd_menu_header),
        "desc": "survey, extract and refine valuable resources."
    },
    "contracts": {
        "func": lambda: contracts_loop(ship_operator,print_cmd_menu_header),
        "desc": "Request new contracts or fulfill your current ones."
    },
    "ship": {
        "func": lambda: ship_menu(ship_operator),
        "desc": "Study and modify your ship;s cargo, crew and capabilities"
    },
    "menu": {
        "func": lambda: use_game_menu(command_menu),
        "desc": "Provide interactive menu of commands."
    },
    "back": {
        "func": lambda: "back",
        "desc": "Return to the previous menu"
    },
    "exit": {
        "func": lambda: "exit",
        "desc": "Quit the game"
    }
}

#==========
def trade_menu(ship_operator:ShipOperator):
    cli_print("trade menu in development")

#==========
def explore_menu(ship_operator:ShipOperator):
    cli_print("explore menu in development")

#==========
def mine_menu(ship_operator:ShipOperator):
    cli_print("mine menu in development")

#==========
def contract_menu(ship_operator:ShipOperator):
    cli_print("contract menu in development")

#==========
def ship_menu(ship_operator:ShipOperator):
    cli_print("ship menu in development")