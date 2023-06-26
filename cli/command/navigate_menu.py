
from src.ship_operator import *
from src.utilities.basic_utilities import time_diff_seconds
from cli_utilities import *
from art.str_formatting import format_waypoint_template
from art.ascii_art import border_med_dash,border_nav_menu
from art.animations import animate_navigation

#==========
ship_operator:ShipOperator

#==========
nav_menu_color = "orange3" #Color used by default in cli_print

#==========
def navigate_loop(ship:ShipOperator) -> bool:
    """Wrapper for command_loop. Initializes the ship_operator object to be used in this command
    menu. Returns True if a command was given to exit the game.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    cli_print(border_nav_menu,nav_menu_color)
    cli_print("Choose a navigation option",nav_menu_color)

    exit = command_loop(navigate_menu,sep=border_nav_menu,color=nav_menu_color)
    if exit: #If player wants to exit, return True to signal to parent menu
        return True

    cli_clear()
    cli_print("Returning to ship command menu...")
    return False

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
    "list": {
        "func": lambda: list_cmds(navigate_menu),
        "desc": "List the commands in this menu."
    },
    "menu": {
        "func": lambda: use_menu(navigate_menu),
        "desc": "Provide interactive menu of commands."
    }
}

#==========
def nav_ship():
    cli_clear()
    print_location()

    #Load data
    data = ship_operator.curr_system
    wp_list = [wp for wp in data['waypoints']]

    cancel_option = "Cancel navigation"
    menu_items = [format_waypoint_template(num,wp) for num,wp in enumerate(wp_list)]
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
    pass

#==========
def warp_ship():
    pass

#==========
def print_location() -> None:
    wp = ship_operator.curr_waypoint
    cli_print(border_med_dash,nav_menu_color)
    cli_print(f"Current Waypoint: {wp['symbol']} ({wp['type']})",nav_menu_color)
    cli_print(border_med_dash,nav_menu_color)