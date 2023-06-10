"""
First version of a basic CLI.
This startup script sets up the game for a Python terminal.
Needs to be run in terminal as "python3 -i startup_cli.py"
"""

import os
from src.base import get_config_callsign
from src.ship_operator import *
from src.art.ascii_art import intro_text

callsign = get_config_callsign()
default_ship = callsign+"-1"



def startup():
    os.system("clear")
    print(intro_text)
    print(f"Welcome back Captain {callsign}\n")
    print(f"Your ship {default_ship} is ready to command.\nEx: ship.curr_system")

def loadShip() -> ShipOperator:
    return ShipOperator(default_ship)


if __name__ == "__main__":
    startup()
    ship = loadShip()
