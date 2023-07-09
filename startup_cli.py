"""
This separate file before the game initializes is to allow the modification of the chosen player.
Can also be done manually (less fun) in the gameinfo.yaml file
"""
# from PyInquirer import prompt
from simple_term_menu import TerminalMenu
from src.base import SpaceTraderConfigSetup, RegisterNewAgent
from src.utilities.custom_types import SpaceFactions
from cli.art.ascii_art import border_long_carat,bootup_image
from rich import print as rprint
import subprocess

#----------
def print_greeting() -> None:
    rprint(f"[cornflower_blue]{border_long_carat}[/cornflower_blue]")
    rprint(f"[yellow]{bootup_image}[/yellow]")
    rprint(f"[cornflower_blue]{border_long_carat}[/cornflower_blue]")

#----------
def set_player() -> None:
    config_setup = SpaceTraderConfigSetup()
    callsigns = config_setup.get_all_callsigns()
    setup_player_option = "[Create New Agent]"
    callsigns.append(setup_player_option)
    choice = prompt_player_select(callsigns,"Please pick your player")
    if choice == setup_player_option:
        choice = setup_new_player()

#----------
def prompt_player_select(callsigns:list[str],title:str) -> str:
    print_greeting()
    terminal_menu = TerminalMenu(callsigns,
                                 title=title,
                                 menu_cursor_style=("fg_green","bold"),
                                 menu_highlight_style=None,
                                 menu_cursor="-> "
                                )
    terminal_menu.show()
    return terminal_menu.chosen_menu_entry

#----------
def setup_new_player() -> str:
    print("Welcome new agent! Which name would you like to go by?")
    id = input("Your name should be in all CAPS and only use letters and hypens.\n> ")
    faction_list = SpaceFactions._member_names_
    faction = prompt_player_select(faction_list,f"Welcome {id}! Now please choose your starting faction:")
    registrant = RegisterNewAgent()
    registrant.register_new_agent(id,faction)
    return id

#----------
if __name__ == "__main__":
    subprocess.run("clear")
    set_player()
    subprocess.run(["python3","cli/main_menu.py"])



