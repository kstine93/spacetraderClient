
from src.ship_operator import *
from src.utilities.basic_utilities import dedup_list
from src.utilities.custom_types import RefinableProduct
from cli_utilities import *
from art.ascii_art import border_med_dash,border_mine_menu
from art.str_formatting import format_survey_template, format_base_hud_template

#==========
ship_operator:ShipOperator

#==========
mine_menu_color = "medium_purple2" #Color used by default in cli_print

#==========
def print_mine_menu_header() -> str:
    print_mine_hud()
    cli_print(border_nav_menu,mine_menu_color)

#==========
def print_mine_hud() -> str:
    flightMode = ship_operator.flightMode
    fuel = ship_operator.fuel
    system = ship_operator.curr_system
    hud = format_base_hud_template(flightMode,system,fuel)
    cli_print(hud)

#==========
def mine_loop(ship:ShipOperator) -> bool:
    """Wrapper for command_loop. Initializes the ship_operator object to be used in this command
    menu. Returns True if a command was given to exit the game.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    cli_print(border_mine_menu,mine_menu_color)
    cli_print("Choose to mine, survey or refine resources, Captain",mine_menu_color)

    exit = command_loop(mine_menu,loop_func=print_mine_menu_header)
    if exit: #If player wants to exit, return True to signal to parent menu
        return True

    cli_clear()
    cli_print("Returning to ship command menu...")
    return False

#==========
mine_menu = {
    "survey": {
        "func": lambda: survey(),
        "desc": "Collect information about resources at your current location."
    },
    "extract": {
        "func": lambda: extract(),
        "desc": "Extract resources from the current location\nwith an optional target resource."
    },
    "refine": {
        "func": lambda: refine(),
        "desc": "Create a new resource from raw resources in cargo.\nRequires refining module."
    },
    "list": {
        "func": lambda: list_cmds(mine_menu),
        "desc": "List the commands in this menu."
    },
    "menu": {
        "func": lambda: use_menu(mine_menu),
        "desc": "Provide interactive menu of commands."
    }
}

#==========
def survey() -> None:
    cooldown_secs = ship_operator.get_cooldown_seconds()
    if cooldown_secs > 0:
        cli_print(f"Cannot survey until cooldown expires in {cooldown_secs} seconds",mine_menu_color)
    else:
        cli_print("Surveying waypoint now...",mine_menu_color)
        ship_operator.survey_waypoint()
    cli_print("Survey list:\n",mine_menu_color)
    list_surveys()

#==========
def list_surveys() -> None:
    survey_list = ship_operator.surveys
    if len(survey_list) == 0:
        cli_print("No surveys collected yet.",mine_menu_color)
    for survey in survey_list:
        cli_print(format_survey_template(survey),mine_menu_color)

#==========
def extract() -> None:
    #QUESTION: Should I filter surveys based on whether they are from the current location?
    #Code will work either way, but we might offer player a surveyed resource not possible at
    #current location...
    #NOTE: It is a bit odd to have the player choose a resource to 'target' and then they get a
    #totally different resource (if another resource in survey). I'm not sure of the best way to
    #solve this though. Make it more clear that we're using a particular survey?
    #I'm actually considering maybe removing my 'optimal survey' code and just prompting
    #the user to select a survey. It's less sophisticated, but it gives some agency back to the
    #user and lets them make some decisions...

    cooldown_secs = ship_operator.get_cooldown_seconds()
    if cooldown_secs > 0:
        cli_print(f"Cannot extract until cooldown expires in {cooldown_secs} seconds",mine_menu_color)
        return None

    menu_items = get_items_in_surveys()

    no_preference_option = "Do not target a resource"
    cancel_option = "Cancel mining"
    menu_items.append(no_preference_option)
    menu_items.append(cancel_option)

    #Prompt user to select item to target in mining:
    survey_menu = create_menu(menu_items,prompt="Try to target a particular surveyed resource?")

    chosen_resource = menu_prompt(survey_menu)
    if chosen_resource == cancel_option:
        return None
    if chosen_resource == no_preference_option:
        chosen_resource = None

    cli_print(f"Using optimal survey to extract {chosen_resource}...")

    #Extract:
    rsc_yield = ship_operator.extract(chosen_resource)
    if rsc_yield is None:
        return None
    cli_print(f"Extracted {rsc_yield['units']} units of {rsc_yield['symbol']}",mine_menu_color)

#==========
def get_items_in_surveys() -> list[str]:
    survey_list = ship_operator.surveys
    rsc_list = []
    for survey in survey_list:
        survey_rscs = [dep['symbol'] for dep in survey['deposits']]
        rsc_list.extend(survey_rscs)
    return dedup_list(rsc_list)

#==========
def refine():
    cooldown_secs = ship_operator.get_cooldown_seconds()
    if cooldown_secs > 0:
        cli_print(f"Cannot refine until cooldown expires in {cooldown_secs} seconds",mine_menu_color)
        return None

    cancel_option = "Cancel refining"
    menu_items = RefinableProduct._member_names_.copy() #Custom type showing all possible values
    menu_items.append(cancel_option)

    refine_menu = create_menu(menu_items,prompt="Try to target a particular surveyed resource?")

    chosen_resource = menu_prompt(refine_menu)
    if chosen_resource == cancel_option:
        return None

    refine_yield = ship_operator.refine(chosen_resource)
    cli_print(f"Refined {refine_yield['units']} units of {refine_yield['tradeSymbol']}",mine_menu_color)

#==========
def print_mine_hud():
    """Placeholder. I would like a function to print a 'HUD' to the top of the terminal showing relevant infos.
    This might be better served by a format string function though...
    Also, need to solve the problem for how I keep this info updated as commands occur."""
    pass