"""Menu for buying and selling resources in markets located across the game world"""

from src.ship_operator import ShipOperator
from src.markets import Markets
from typing import Callable
from cli_utilities import *
from info_menu import print_hud, info_loop
from contracts_menu import contracts_loop
from art.ascii_art import border_trade_menu

#==========
ship_operator:ShipOperator
market = Markets()

#==========
trade_menu_color = "green3" #Color used by default in cli_print

#==========
def print_trade_menu_header() -> None:
    print_hud(ship_operator)
    cli_print(border_trade_menu,trade_menu_color)

#==========
def trade_loop(ship:ShipOperator,returnHeaderFunc:Callable) -> CliCommand | None:
    """Wrapper for command_loop. Initializes the ship_operator object to be used in this command
    menu. Returns True if a command was given to exit the game.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    print_trade_menu_header()
    cli_print("Choose to buy, sell or look for profitable opportunities.",trade_menu_color)

    res = command_loop(trade_menu,loop_func=print_trade_menu_header)
    if res == "exit": #If player wants to exit, return True to signal to parent menu
        return res

    cli_clear()
    cli_print("Returning to ship command menu...")
    returnHeaderFunc()
    return None

#==========
trade_menu = {
    "market": {
        "func": lambda: get_curr_market(),
        "desc": "See the market goods and prices at the current waypoint."
    },
    "buy": {
        "func": lambda: buy_commodity(),
        "desc": "Buy something from the market at the current waypoint."
    },
    "sell": {
        "func": lambda: sell_commodity(),
        "desc": "Sell something from your ship's cargo at the market at the current waypoint."
    },
    "margins": {
        "func": lambda: get_profit_margins(),
        "desc": "Find profitable markets for a specific commodity or generally."
    },
    "info": {
        "func": lambda: info_loop(ship_operator,print_trade_menu_header),
        "desc": "Inspect your ship's cargo, crew and capabilities"
    },
    "contracts": {
        "func": lambda: contracts_loop(ship_operator,print_trade_menu_header),
        "desc": "See available and current contracts - and fulfill them"
    },
    "menu": {
        "func": lambda: use_game_menu(trade_menu),
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
def get_curr_market() -> None:
    wp = ship_operator.currWaypoint['symbol']
    mkt = market.get_market(wp)
    cli_print(mkt)

    '''
    Desired behavior:
    1. Get current waypoint
    2. Call 'get_market' on current waypoint
    3. format and print information on market
        3a. Note: Should be done in str_Formatting.py of course
        3b. Note: Should be fairly compact printout - otherwise could get quite long (maybe only 1
            line per item with both sell +_ buy prices)
        3c. Note: Is there any risk of the price information I want not being available?
            3ci. I think this is only the case if I'm getting a market from another location- which
                is not relevant except in full game margin calculation.

    NOTE: I'm liking more and more the idea of just using a 'menu' for this rather than string
        formatting- I can put buy/sell prices in the preview... Think about this more...

    '''
    pass

#==========
def buy_commodity() -> None:
    '''
    Desired behavior:
    1. Get information on what is available in the current market
    2. format items into understandable menu (with any preview info?)
    3. Allow player to choose item and THEN type quantity (showing possible range)
    4. execute 'purchase' endpoint
    5. Provide confirmation of success
    6. Reload cargo (might be done automatically? See ship_operator class)
    '''
    pass

#==========
def sell_commodity() -> None:
    '''
    Desired behavior:
    1. Get information on what is available in cargo of the ship
    2. format items into understandable menu (with any preview info?) (same as 'buy')
    3. Allow player to choose item and THEN type quantity (showing possible range) (same as 'buy')
    4. execute 'sell' endpoint
    5. Provide confirmation of success
    6. Reload cargo (might be done automatically? See ship_operator class) (same as 'buy')
    '''
    pass

#==========
def get_profit_margins() -> None:
    '''
    Desired behavior:
    1. Prompt player to 'get 5 best profit margins of visited markets' or to select a specific
        commodity they want to find the best buy market and best sell market for
    2. Run method already written in markets.py
    3. format and print out result in a nice way (str_formatting.py)
    '''
    pass