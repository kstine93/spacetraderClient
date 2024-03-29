
"""Menu for mining resources from the current waypoint or refining resources in ship's cargo hold."""

from src.ship_operator import *
from typing import Callable
from src.utilities.custom_types import RefinableProduct
from cli_utilities import *
from info_menu import print_hud, info_loop
from contracts_menu import contracts_loop
from art.ascii_art import border_mine_menu
from art.str_formatting import format_survey_template, format_surveyMenu_template

#==========
ship_operator:ShipOperator

#==========
mine_menu_color = "medium_purple2" #Color used by default in cli_print

#==========
def print_mine_menu_header() -> None:
    print_hud(ship_operator)
    cli_print(border_mine_menu,mine_menu_color)

#==========
def mine_loop(ship:ShipOperator,returnHeaderFunc:Callable) -> CliCommand | None:
    """Wrapper for command_loop. Initializes the ship_operator object to be used in this command
    menu. Returns True if a command was given to exit the game.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    print_mine_menu_header()
    cli_print("Choose to mine, survey or refine resources, Captain",mine_menu_color)

    res = command_loop(mine_menu,loop_func=print_mine_menu_header)
    if res == "exit": #If player wants to exit, return True to signal to parent menu
        return res

    cli_clear()
    cli_print("Returning to ship command menu...")
    returnHeaderFunc()
    return None

#==========
mine_menu = {
    "survey": {
        "func": lambda: survey(),
        "desc": "Collect information about resources at your current location."
    },
    "extract": {
        "func": lambda: extract_choose_survey(),
        "desc": "Extract resources from the current location\nwith an optional target resource."
    },
    "refine": {
        "func": lambda: refine(),
        "desc": "Create a new resource from raw resources in cargo.\nRequires refining module."
    },
    "info": {
        "func": lambda: info_loop(ship_operator,print_mine_menu_header),
        "desc": "Inspect your ship's cargo, crew and capabilities"
    },
    "contracts": {
        "func": lambda: contracts_loop(ship_operator,print_mine_menu_header),
        "desc": "See available and current contracts - and fulfill them"
    },
    "menu": {
        "func": lambda: use_game_menu(mine_menu),
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
def extract_choose_survey() -> None:

    cooldown_secs = ship_operator.get_cooldown_seconds()
    if cooldown_secs > 0:
        cli_print(f"Cannot extract until cooldown expires in {cooldown_secs} seconds",mine_menu_color)
        return None

    #Filtering surveys for those relevant to current waypoint:
    survey_list = ship_operator.get_surveys_current_waypoint()

    if survey_list is None:
        #If no surveys, extract without surveys:
        cli_print("No survey data found for current waypoint. Extracting without survey...",mine_menu_color)
        rsc_yield = ship_operator.extract()
    else:
        menu_items = [format_surveyMenu_template(num,sur) for num,sur in enumerate(survey_list)]

        #Adding other menu options:
        no_preference_option = "Do not use a survey"
        cancel_option = "Cancel mining"

        menu_items.append(no_preference_option)
        menu_items.append(cancel_option)
        #Making survey_list items & order consistent with menu_items
        survey_list.append(no_preference_option)
        survey_list.append(cancel_option)


        #Prompt user to select waypoint + process:
        '''NOTE: When using preview, the menu items are truncated at the bar ("|"). In this case,
        returning the INDEX rather than the VALUE of the chosen option helps avoid mis-matched items'''
        survey_menu = create_menu(menu_items
                            ,prompt="Target resources with a certain survey?"
                            ,preview_command=lambda x: x #Should print traits to preview box
                            ,preview_title="Survey overview:"
                            ,preview_size=0.25)

        chosen_survey_index = menu_prompt(survey_menu,index=True)
        chosen_survey = survey_list[chosen_survey_index]

        if chosen_survey == cancel_option:
            return None
        elif chosen_survey == no_preference_option:
            rsc_yield = ship_operator.extract()
        else:
            rsc_yield = ship_operator.extract(chosen_survey)

    if rsc_yield is None:
        return None
    cli_print(f"Extracted {rsc_yield['units']} units of {rsc_yield['symbol']}",mine_menu_color)

#==========
def refine() -> None:
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