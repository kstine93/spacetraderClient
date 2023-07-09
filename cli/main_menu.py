"""Main menu of the spacetrader CLI game"""


#==========
"""
Adding parent directory to Python path so that 'src' imports are possible.
TODO: Make a more graceful import solution than this.
"""
#==========
import os
import sys
PROJECT_ROOT = os.path.abspath(os.path.join(
                os.path.dirname(__file__),
                os.pardir)
)
sys.path.append(PROJECT_ROOT)

#==========
import typer
from src.contracts import Contracts
from command_menu import ship_command_loop
from cli_utilities import *
from command_menu import ship_command_loop
from common_cmds import list_contracts

#==========
app = typer.Typer()
contracts = Contracts()

#==========
main_menu_color = "cornflower_blue" #Color used by default in cli_print

#==========
def print_main_menu_header() -> str:
    cli_print(border_main_menu,main_menu_color)

#==========
def main_menu_loop() -> None:
    """Wrapper for command_loop. First menu in the game. Once this function ends the game ends.
    """
    cli_clear()
    print_start_screen()
    cli_print(f"Welcome back, Captain.\n","yellow")
    prompt = "Use 'list' or 'menu' to get help, and 'exit' to quit."
    command_loop(main_menu,prompt,print_main_menu_header)
    shutdown()

#==========
def print_start_screen() -> None:
    cli_print(border_long_carat,main_menu_color)
    cli_print(bootup_image,"yellow")
    cli_print(border_long_carat,main_menu_color)

#==========
def shutdown() -> None:
    cli_clear()
    print_start_screen()
    cli_print("Goodbye, Captain.\n","yellow")

#==========
main_menu = {
    "contracts": {
        "func": lambda: list_contracts(),
        "desc": "List all active contracts."
    },
    "command": {
        "func": lambda: ship_command_loop(),
        "desc": "Command one of your ships - play the game!"
    },
    "explore": {
        "func": lambda: explore_systems(),
        "desc": "Learn more about the galaxy you're playing in."
    },
    "list": {
        "func": lambda: list_cmds(main_menu),
        "desc": "List the commands in this menu."
    },
    "menu": {
        "func": lambda: use_menu(main_menu),
        "desc": "Provide interactive menu of commands."
    }
}

# #==========
# def list_contracts(color:str="chartreuse2") -> None:
#     """Function to print out all contracts for a """
#     data = contracts.list_all_contracts()
#     cli_print(border_contract_section,color)
#     for contract in data.values():
#         cli_print(format_contract_template(contract),color)

#==========
def explore_systems() -> None:
    print("Not yet implemented - sorry!")


#/////////////////////////
if __name__ == "__main__":
    typer.run(main_menu_loop)