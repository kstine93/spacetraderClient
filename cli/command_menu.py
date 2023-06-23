"""Holder of most commands for CLI"""
from cli.cli_utilities import *
from cli.command.navigate_menu import *
from src.ship_operator import *


"""
TODO: Make a base version of my menu which always has a "< Exit menu" option to go back to command loop
"""
ship_operator:ShipOperator


#==========
def ship_command_loop(ship:str) -> None:
    global ship_operator
    ship_operator = ShipOperator(ship)
    cli_print(border_cmd_menu,color="deep_pink4")
    cli_print(f"Welcome aboard {ship}, Captain")
    command_loop(command_menu,sep=border_cmd_menu,color="deep_pink4")
    cli_print("Returning to main menu...")

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
        "func": lambda: mine_menu(ship_operator),
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