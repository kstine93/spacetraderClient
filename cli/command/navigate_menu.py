
from src.ship_operator import *
from src.utilities.basic_utilities import time_diff_seconds
from src.utilities.custom_types import NavSpeed
from cli_utilities import *
from typing import Callable
from art.str_formatting import format_waypoint_template, format_system_template
from art.ascii_art import border_med_dash, border_nav_menu
from art.animations import animate_navigation
from info_menu import print_hud, info_loop
from contracts_menu import contracts_loop

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
        "desc": "Inspect your ship's cargo, crew and capabilities"
    },
    "contracts": {
        "func": lambda: contracts_loop(ship_operator,print_nav_menu_header),
        "desc": "See available and current contracts - and fulfill them"
    },
    "menu": {
        "func": lambda: use_game_menu(navigate_menu),
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
    data = ship_operator.currSystem
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
    gate_opt = "use stationary Jump Gate"
    drive_opt = "use ship's onboard Jump Drive"
    jump_menu = create_menu([gate_opt,drive_opt],prompt="Choose how to jump to new system:")
    jump_opt = menu_prompt(jump_menu)
    if jump_opt == drive_opt:
        #Checking if player has jump drive and antimatter
        if "JUMP_DRIVE" not in [mod['symbol'] for mod in ship_operator.shipModules]:
            cli_print("Your ship has no 'JUMP_DRIVE' module. Aborting jump.")
            return
        if "ANTIMATTER" not in [item['symbol'] for item in ship_operator.cargo['inventory']]:
            cli_print("Your ship has no antimatter for its Jump Drive. Aborting Jump.")
            return
    elif jump_opt == gate_opt:
        if ship_operator.currWaypoint["type"] != "JUMP_GATE":
            cli_print("Your ship is not located at a Jump Gate. Aborting jump.")
            return

    chosen_sys = pick_nearbySystem_from_menu()
    ship_operator.jump(chosen_sys['symbol'])
    cli_print(f"Jump successful. Welcome to {chosen_sys}, Captain","red")

#==========
def pick_nearbySystem_from_menu() -> str:
    """Pick system from 'nearbySystem' attribute"""
    if not ship_operator.nearbySystems:
        ship_operator.scan_systems()
    sys_list = sorted(ship_operator.nearbySystems,key=lambda x: x['distance'])
    menu_items = [format_system_template(num,sys) for num,sys in enumerate(sys_list)]
    cancel_option = "Cancel navigation"
    menu_items.append(cancel_option)
    sys_list.append(cancel_option) #Making wp_list items & order consistent with menu_items

    sys_menu = create_menu(menu_items
                          ,prompt="Choose a system to jump to:"
                          ,preview_command=lambda x: x #Should print traits to preview box
                          ,preview_title="Distance to this system:"
                          ,preview_size=0.15)
    chosen_sys_index = menu_prompt(sys_menu,index=True)
    chosen_sys = sys_list[chosen_sys_index]
    if chosen_sys == cancel_option:
        return None
    return chosen_sys

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
        options = NavSpeed._member_names_
        menu = create_menu(options,prompt=f"Set your new speed (current: {ship_operator.flightMode}")
        new_speed = menu_prompt(menu)
        ship_operator.set_speed(new_speed)

#==========
def print_location() -> None:
    wp = ship_operator.currWaypoint
    cli_print(border_med_dash,nav_menu_color)
    cli_print(f"Current Waypoint: {wp['symbol']} ({wp['type']})",nav_menu_color)
    cli_print(border_med_dash,nav_menu_color)