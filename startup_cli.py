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
config_setup = SpaceTraderConfigSetup()

#----------
def print_greeting() -> None:
    rprint(f"[cornflower_blue]{border_long_carat}[/cornflower_blue]")
    rprint(f"[yellow]{bootup_image}[/yellow]")
    rprint(f"[cornflower_blue]{border_long_carat}[/cornflower_blue]")

#----------
def set_player(print_msg=True) -> bool:
    """Allows user to choose an agent to use for the game - as well as remove players or cancel
    game startup"""
    callsigns = config_setup.get_all_callsigns()
    setup_player_option = "[Create New Agent]"
    remove_player_option = "[Remove an Agent]"
    exit_option = "[Exit Game]"
    callsigns.append(setup_player_option)
    callsigns.append(remove_player_option)
    callsigns.append(exit_option)
    choice = select_from_menu(callsigns,"Please pick your player", print_greeting_msg=print_msg)
    if choice == setup_player_option:
        setup_new_player()
        #Once new player is made, recurse to load new callsign and prompt user to pick from the list
        set_player(print_msg=False)
        return True
    elif choice == remove_player_option:
        remove_player()
        return False
    elif choice == exit_option:
        rprint("[yellow]== Exiting game ==[/yellow]")
        return False
    return True

#----------
def select_from_menu(menu_options:list[str],title:str,print_greeting_msg:bool=True) -> str:
    if print_greeting_msg:
        print_greeting()
    terminal_menu = TerminalMenu(menu_options,
                                 title=title,
                                 menu_cursor_style=("fg_green","bold"),
                                 menu_highlight_style=None,
                                 menu_cursor="-> "
                                )
    terminal_menu.show()
    return terminal_menu.chosen_menu_entry

#----------
def remove_player() -> None:
    msg = "Choose an agent to REMOVE FROM THE GAME.\nYou will no longer be able to select this player."
    callsigns = config_setup.get_all_callsigns()
    cancel_option = "[Cancel]"
    callsigns.append(cancel_option)
    msg = "Choose an agent to REMOVE FROM THE GAME.\nYou will no longer be able to select this player."
    agent = select_from_menu(callsigns,msg,False)
    if agent != cancel_option:
        config_setup.remove_agent_details(agent)

#----------
def setup_new_player() -> None:
    print("Welcome new agent! Which name would you like to go by?")
    id = input("Your name should be in all CAPS and only use letters and hypens.\n> ")
    faction_list = SpaceFactions._member_names_
    faction = select_from_menu(faction_list,
                               f"---\nWelcome {id}! Now please choose your starting faction:",
                               print_greeting_msg = False)
    registrant = RegisterNewAgent()
    res = registrant.register_new_agent(id,faction)
    if res:
        #if registration is a success, print confirmation message.
        rprint(" -- New player setup complete --\n")
    else:
        #If registration fails, RegisterNewAgent will print out error response. Printing spacer:
        rprint(" ----- ")

#----------
if __name__ == "__main__":
    subprocess.run("clear")
    player_set = set_player()
    if player_set == True:
        subprocess.run(["python3","cli/main_menu.py"])
    #Note: Implicitly exiting game if the 'player_set' action failed to set a player
    #(e.g., if the user decided to remove a player, no player is set).



