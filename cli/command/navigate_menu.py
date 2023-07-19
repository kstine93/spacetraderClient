
from src.ship_operator import *
from src.utilities.basic_utilities import time_diff_seconds
from cli_utilities import *
from typing import Callable
from art.str_formatting import format_waypoint_template
from art.ascii_art import border_med_dash, border_nav_menu
from art.animations import animate_navigation
from common_cmds import print_hud, info_loop

#==========
ship_operator:ShipOperator

#==========
nav_menu_color = "orange3" #Color used by default in cli_print

#==========
def print_nav_menu_header() -> str:
    print_hud(ship_operator)
    cli_print(border_nav_menu,nav_menu_color)

#==========
def navigate_loop(ship:ShipOperator,returnHeaderFunc:Callable) -> CliCommand | None:
    """Wrapper for command_loop. Initializes the ship_command_prompt() operator object to be used in this command
    menu. Returns True if a command was given to exit the game.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    print_nav_menu_header()
    cli_print("Choose a navigation option",nav_menu_color)

    res = command_loop(navigate_menu,loop_func=print_nav_menu_header)
    if res == "exit":
        return res

    cli_clear()
    cli_print("Returning to ship command menu...")
    returnHeaderFunc()
    return None

#==========
navigate_menu = {
    "nav": {
        "func": lambda: nav_ship(),
        "desc": "Navigate your ship to a new location."
    },
    "jump": {
        "func": lambda: jump_ship(),
        "desc": "Purchase, sell and study profitable markets"
    },
    "warp": {
        "func": lambda: warp_ship(),
        "desc": "Learn more about surrounding ships, waypoints and systems."
    },
    "speed": {
        "func": lambda: set_speed(),
        "desc": "Learn more about surrounding ships, waypoints and systems."
    },
    "info": {
        "func": lambda: info_loop(ship_operator,print_nav_menu_header),
        "desc": "Show information about the ship related to mining!"
    },
    "list": {
        "func": lambda: list_cmds(navigate_menu),
        "desc": "List the commands in this menu."
    },
    "menu": {
        "func": lambda: use_menu(navigate_menu),
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
def nav_ship() -> None:
    # print_location()

    #Load data
    data = ship_operator.curr_system
    wp_list = [wp for wp in data['waypoints']]

    menu_items = [format_waypoint_template(num,wp) for num,wp in enumerate(wp_list)]
    cancel_option = "Cancel navigation"
    menu_items.append(cancel_option)
    wp_list.append(cancel_option) #Making wp_list items & order consistent with menu_items

    #Prompt user to select waypoint + process:
    '''NOTE: When using preview, the menu items are truncated at the bar ("|"). In this case,
    returning the INDEX rather than the VALUE of the chosen option helps avoid mis-matched items'''
    wp_menu = create_menu(menu_items
                          ,prompt="Choose a waypoint to navigate to:"
                          ,preview_command=lambda x: x #Should print traits to preview box
                          ,preview_title="Waypoint traits:"
                          ,preview_size=0.25)
    chosen_wp_index = menu_prompt(wp_menu,index=True)
    chosen_wp = wp_list[chosen_wp_index]
    if chosen_wp == cancel_option:
        return None

    #Navigate:
    ship_operator.nav(chosen_wp['symbol'])
    #Animating + showing travel time
    seconds_to_arrival = time_diff_seconds(ship_operator.arrivalTime)
    animate_navigation(seconds_to_arrival)

#==========
def jump_ship():
    """
    Steps:
    1. Check if ship at jump gate
        1a. If yes, scan systems and provide list to choose from (ALPHA)
    2. If no, check if jump drive installed on ship
        1a. If yes, check if we have antimatter
            1ai. If yes, ask if player wants to use antimatter + jump drive
                1ai1. If yes, scan systems and provide list to choose from (ALPHA)
            1aii. If no, cancel command
        1b. If no, Inform player no antimatter present - they must nav to jump gate first (BETA)
    3. If no jump drive, inform player they must nav to jump gate first (BETA)

    """
    pass

#==========
def warp_ship():
    """
    Steps:
    1. check if warp drive installed on ship
        1a. If yes, provide list of waypoints (NOTE: Not sure how to get this... There's no endpoint for this.
            I could show a list of waypoints I've already been to, maybe? Showing a list of ALL waypoints is not feasible..)
    3. If no warp drive, inform player they cannot warp - use 'jump' and 'nav' instead.

    """
    pass

#==========
def set_speed():
    pass

#==========
def print_location() -> None:
    wp = ship_operator.curr_waypoint
    cli_print(border_med_dash,nav_menu_color)
    cli_print(f"Current Waypoint: {wp['symbol']} ({wp['type']})",nav_menu_color)
    cli_print(border_med_dash,nav_menu_color)

# #==========
# def get_info_navigate():
#     """Print out HUD relevant to mining on the CLI"""
#     print_crew_info(ship_operator)
#     print_ship_info(ship_operator)
#     print_ship_mount_info(ship_operator)
#     print_ship_module_info(ship_operator)
#     print_contracts_info()