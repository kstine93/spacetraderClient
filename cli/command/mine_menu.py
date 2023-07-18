
from src.ship_operator import *
from src.utilities.custom_types import RefinableProduct
from cli_utilities import *
from common_cmds import (print_hud,
                         print_contracts_info,
                         print_general_info,
                         print_ship_info,
                         print_ship_mount_info,
                         print_ship_module_info,
                         print_cargo_info,
                         print_crew_info
)
from art.ascii_art import border_mine_menu
from art.str_formatting import format_survey_template, format_surveyMenu_template

#==========
ship_operator:ShipOperator

#==========
mine_menu_color = "medium_purple2" #Color used by default in cli_print

#==========
def print_mine_menu_header() -> str:
    print_hud(ship_operator)
    cli_print(border_mine_menu,mine_menu_color)

#==========
def mine_loop(ship:ShipOperator) -> bool:
    """Wrapper for command_loop. Initializes the ship_operator object to be used in this command
    menu. Returns True if a command was given to exit the game.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    print_mine_menu_header()
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
        "func": lambda: extract_choose_survey(),
        "desc": "Extract resources from the current location\nwith an optional target resource."
    },
    "refine": {
        "func": lambda: refine(),
        "desc": "Create a new resource from raw resources in cargo.\nRequires refining module."
    },
    "info": {
        "func": lambda: get_info_mine(),
        "desc": "Show information about the ship related to mining!"
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
        if chosen_survey == no_preference_option:
            rsc_yield = ship_operator.extract()
        rsc_yield = ship_operator.extract(chosen_survey)

    if rsc_yield is None:
        return None
    cli_print(f"Extracted {rsc_yield['units']} units of {rsc_yield['symbol']}",mine_menu_color)


"""
NOTE: I have commented out the function below because it represents an alternate version of
resource-extraction that I'm not sure I want to fully get rid of yet...
This version allows the user to just select a certain resource to mine for (from a list of
resources in the collected 'surveys'). However, this often resulted in the player choosing 1
resource, but collecting another since the survey that was eventually used had multiple resources
possible. This was determined to be too counter-intuitive, so now the player just chooses the survey
they want to apply to extraction (or none).
"""
# #==========
# def extract_target_resource() -> None:
#     #QUESTION: Should I filter surveys based on whether they are from the current location?
#     #Code will work either way, but we might offer player a surveyed resource not possible at
#     #current location...
#     #NOTE: It is a bit odd to have the player choose a resource to 'target' and then they get a
#     #totally different resource (if another resource in survey). I'm not sure of the best way to
#     #solve this though. Make it more clear that we're using a particular survey?
#     #I'm actually considering maybe removing my 'optimal survey' code and just prompting
#     #the user to select a survey. It's less sophisticated, but it gives some agency back to the
#     #user and lets them make some decisions...

#     cooldown_secs = ship_operator.get_cooldown_seconds()
#     if cooldown_secs > 0:
#         cli_print(f"Cannot extract until cooldown expires in {cooldown_secs} seconds",mine_menu_color)
#         return None

#     menu_items = get_items_in_surveys()

#     no_preference_option = "Do not target a resource"
#     cancel_option = "Cancel mining"
#     menu_items.append(no_preference_option)
#     menu_items.append(cancel_option)

#     #Prompt user to select item to target in mining:
#     survey_menu = create_menu(menu_items,prompt="Try to target a particular surveyed resource?")

#     chosen_resource = menu_prompt(survey_menu)
#     if chosen_resource == cancel_option:
#         return None
#     if chosen_resource == no_preference_option:
#         chosen_resource = None

#     cli_print(f"Using optimal existing survey to extract {chosen_resource}...")

#     #Extract:
#     rsc_yield = ship_operator.extract(chosen_resource)
#     if rsc_yield is None:
#         return None
#     cli_print(f"Extracted {rsc_yield['units']} units of {rsc_yield['symbol']}",mine_menu_color)

# #==========
# def get_items_in_surveys() -> list[str]:
#     survey_list = ship_operator.surveys
#     rsc_list = []
#     for survey in survey_list:
#         survey_rscs = [dep['symbol'] for dep in survey['deposits']]
#         rsc_list.extend(survey_rscs)
#     return dedup_list(rsc_list)

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
def get_info_mine():
    """Print out HUD relevant to mining on the CLI"""
    print_general_info(ship_operator)
    print_ship_info(ship_operator)
    print_cargo_info(ship_operator,mine_menu_color)
    print_crew_info(ship_operator)
    print_contracts_info()
    print_ship_mount_info(ship_operator)
    print_ship_module_info(ship_operator)
    print_contracts_info()