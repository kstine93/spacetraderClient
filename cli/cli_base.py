"""Holder of most commands for CLI"""
from .cli_utilities import *
from PyInquirer import prompt, print_json, Separator
from src.ship_operator import *

# if __name__ == '__main__':
#     if __package__ is None:
#         import sys
#         from os import path
#         sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
#         from src.ship_operator import *
#     else:
#         from ..src.ship_operator import *

ship_op = ShipOperator("AMBROSIUS-RITZ-1")
#----------
def list_cmds():
    rprint("I guess this works")


#----------
def bootup():
    """
    Steps of bootup:
    1. Display pretty UI
    2. Figure out PLAYER (dependent only on API key)
        2a. Ask player to input API key / decrypt API key
        2b. Pull agent data with API key.
        2c. Greet agent by name
    3. Present agent-level options:
        3a. check contracts
        3b. check markets
        3c. command ship
        3d. (check systems?? - not really yet implemented)
    4. Allow player to select one of the ships associated with their agent (if more than 1)
    5. Offer ship-level commands

    CHANGES NEEDED:
    1. API key needs to be stored differently. The current
    """
    bootup_ui()


"""
TODO: Make a base version of my menu which always has a "< Exit menu" option to go back to command loop

NOTE: It would be great to show users what each command means... but not sure it's possible to include
a description or if it would be wise given line space. Maybe just have more descriptive command names?
"""
module_list_question = [
        {
            'type': 'list',
            'name': 'commands',
            'message': 'Choose your next action, Captain: ',
            'choices': [
                        {'name': 'navigate'},
                        {'name': 'survey'},
                        {'name': 'query'},
            ],
        }
    ]

def pick():
    username = prompt(module_list_question)
    cli_print(border_med_equals,"yellow")

def nav():
    pass