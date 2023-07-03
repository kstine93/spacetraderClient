"""Holder of most commands for CLI"""
from src.ship_operator import *
from src.ships import Ships
from cli_utilities import *
from command.navigate_menu import navigate_loop
from command.mine_menu import mine_loop

#==========
ship_operator:ShipOperator

#==========
cmd_menu_color = "deep_pink4"

#==========
def pick_ship():
    ships = Ships()
    data = ships.list_all_ships()
    ship_list = list(data.keys())
    if len(ship_list) > 1:
        ship_menu = create_menu(ship_list,prompt="Choose a ship to command, Captain:")
        chosen_ship = menu_prompt(ship_menu)
    else:
        chosen_ship = ship_list[0]
    return chosen_ship

#==========
def ship_command_loop() -> bool:
    ship = pick_ship()
    cli_clear()
    cli_print("Loading ship details...",cmd_menu_color)

    global ship_operator
    ship_operator = ShipOperator(ship)

    cli_print(border_cmd_menu,color=cmd_menu_color)
    cli_print(f"Welcome aboard {ship}, Captain")

    exit = command_loop(command_menu,sep=border_cmd_menu,color=cmd_menu_color)
    if exit: #If player wants to exit, return True to signal to parent menu
        return True

    cli_clear()
    cli_print("Returning to main menu...")
    return False

#==========
command_menu = {
    "navigate": {
        "func": lambda: navigate_loop(ship_operator),
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
        "func": lambda: mine_loop(ship_operator),
        "desc": "survey, extract and refine valuable resources."
    },
    "contracts": {
        "func": lambda: explore_menu(ship_operator),
        "desc": "Request new contracts or fulfill your current ones."
    },
    "ship": {
        "func": lambda: ship_menu(ship_operator),
        "desc": "Study and modify your ship;s cargo, crew and capabilities"
    },
    "list": {
        "func": lambda: list_cmds(command_menu),
        "desc": "List the commands in this menu."
    },
    "menu": {
        "func": lambda: use_menu(command_menu),
        "desc": "Provide interactive menu of commands."
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