from .cli_base import *

#----------
command_map = {
    "nav": {
        "func": lambda: pick(),
        "desc": "Navigate a ship to a new waypoint or system."
    },
    "list": {
        "func": lambda: list_cmds(),
        "desc": "list all possible commands"
    }
}

#----------
nav_commands = {
    "nav": {
        "func": lambda: pick(),
        "desc": "Navigate a ship to a new waypoint or system."
    }
}

"""
Commands:

Util:
- list ships
- command ship
- log out agent

Game:
- trading
    - get market
    - get price margin
    - find best price margins
- navigation
    - nav ship
        - to a waypoint in system (menu)
    - jump ship
        - to a system in range (menu)
    - warp ship
        - to a waypoint in range (can I provide menu for this??)
- contracts
    - check contract
    - list available contracts
    - negotiate new contract
    - deliver contract (also checks if we can fulfill contract maybe)
- explore
    - list waypoints
    - list systems

"""