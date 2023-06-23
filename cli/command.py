"""Holder of most commands for CLI"""
from .cli_utilities import *
from src.ship_operator import *


"""
TODO: Make a base version of my menu which always has a "< Exit menu" option to go back to command loop
"""
ship_operator:ShipOperator

#==========
def startup_ship_command(ship:str):
    global ship_operator
    ship_operator = ShipOperator(ship)
    cli_print(f"Welcome aboard {ship}, Captain")
    ship_command_loop()


#==========
def ship_command_loop() -> None:
    command_loop(command_menu)
    cli_print("Returning to main menu...")

#==========
command_menu = {
    "navigate": {
        "func": lambda: navigate_menu(),
        "desc": "Navigate your ship to a new location."
    },
    "trade": {
        "func": lambda: trade_menu(),
        "desc": "Purchase, sell and study profitable markets"
    },
    "explore": {
        "func": lambda: explore_menu(),
        "desc": "Learn more about surrounding ships, waypoints and systems."
    },
    "mine": {
        "func": lambda: mine_menu(),
        "desc": "survey, extract and refine valuable resources."
    },
    "contracts": {
        "func": lambda: explore_menu(),
        "desc": "Request new contracts or fulfill your current ones."
    },
    "ship": {
        "func": lambda: mine_menu(),
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
def navigate_menu():
    cli_print("Nav menu in development")

#==========
def trade_menu():
    cli_print("trade menu in development")

#==========
def explore_menu():
    cli_print("explore menu in development")

#==========
def mine_menu():
    cli_print("mine menu in development")

#==========
def contract_menu():
    cli_print("contract menu in development")

#==========
def ship_menu():
    cli_print("ship menu in development")