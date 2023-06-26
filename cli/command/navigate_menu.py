
from src.ship_operator import *
from src.utilities.basic_utilities import time_diff_seconds
from cli_utilities import *
from art.str_formatting import format_waypoint_template
from art.ascii_art import border_med_carat,border_nav_menu
from art.animations import animate_navigation

ship_operator:ShipOperator

#==========
def navigate_loop(ship:ShipOperator):
    cli_clear()
    global ship_operator
    ship_operator = ship
    cli_print(border_nav_menu,"orange3")
    command_loop(navigate_menu,sep=border_nav_menu,color="orange3")
    cli_clear()
    cli_print("Returning to ship command menu...")


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
    cancel_option = "Cancel navigation"

    #Load data
    data = ship_operator.curr_system
    wp_list = [wp for wp in data['waypoints']]

    #Create nicely-formatted versions of waypoints for nicer menu options:
    enum_wp_list = list(enumerate(wp_list))
    wp_lookup = {}
    for enum_wp in enum_wp_list:
        #Lookup table allows us to have relationship between raw waypoint and formatted menu item.
        (num,wp) = enum_wp
        key = format_waypoint_template(num,wp)
        val = wp['symbol']
        wp_lookup.update({key:val})
    # menu_enum_wp_list = [format_waypoint_template(num,wp) for num,wp in enum_wp_list]
    menu_items = list(wp_lookup.keys())
    menu_items.append(cancel_option)
    #Prompt user to select waypoint + process:
    wp_menu = create_menu(menu_items,prompt="Choose a waypoint to navigate to:")
    chosen_wp = menu_prompt(wp_menu)
    if chosen_wp == cancel_option:
        return None

    #Navigate:
    nav_wp = wp_lookup[chosen_wp]
    ship_operator.nav(nav_wp)
    #Animating + showing travel time
    seconds_to_arrival = time_diff_seconds(ship_operator.arrivalTime)
    animate_navigation(seconds_to_arrival)


#==========
def print_waypoints(enum_wp_list:list[tuple[int,dict]]) -> None:
    for item in enum_wp_list:
        (number, waypoint_dict) = item
        cli_print(format_waypoint_template(number,waypoint_dict),"chartreuse2")

def jump_ship():
    pass

def warp_ship():
    pass