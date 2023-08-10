"""Menu for buying and selling resources in markets located across the game world"""

from src.ship_operator import ShipOperator
from src.markets import Markets
from typing import Callable
from cli_utilities import *
from info_menu import print_hud, info_loop
from contracts_menu import contracts_loop
from art.ascii_art import border_trade_menu
from art.str_formatting import format_market_info_template, format_margin_info_template

#==========
ship_operator:ShipOperator
market = Markets()
market_items_list:list[dict]

#==========
trade_menu_color = "green3" #Color used by default in cli_print

#==========
def print_trade_menu_header() -> None:
    print_hud(ship_operator)
    cli_print(border_trade_menu,trade_menu_color)

#==========
def load_market_data() -> None:
    """NOTE: Loading in market as stable global variable. Only works so long as there is no chance
    the player will move locations while staying in this menu (which is always true as of the
    creation of this function."""
    waypoint = ship_operator.currWaypoint['symbol']
    current_market = market.get_market(waypoint)

    market_info = list(current_market.values())[0]

    global market_items_list
    market_items_list = market_info['tradeGoods']

#==========
def get_price(item:str,buyPrice:bool) -> int:
    key = "purchasePrice" if buyPrice else "sellPrice"
    price = [x[key] for x in market_items_list if x['symbol'] == item]
    price = price[0]
    return int(price)

#==========
def get_buy_price(item):
    return get_price(item,True)

#==========
def get_sell_price(item):
    return get_price(item,False)

#==========
def trade_loop(ship:ShipOperator,returnHeaderFunc:Callable) -> CliCommand | None:
    """Wrapper for command_loop. Initializes the ship_operator object to be used in this command
    menu. Returns True if a command was given to exit the game.
    """
    cli_clear()

    global ship_operator
    ship_operator = ship

    load_market_data()

    print_trade_menu_header()

    prompt = "Choose to buy, sell or look for profitable opportunities."
    res = command_loop(trade_menu,prompt,loop_func=print_trade_menu_header)
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
def pick_item_from_market_menu(market_items:list[dict],prompt:str) -> str:
    menu_items = []
    for item in market_items:
        preview = format_market_info_template(item)
        preview = preview.replace("|","\|") #For preview in menu, any normal bars must be escaped.
        menu_items.append(f"{item['symbol']}|{preview}")

    contract_menu = create_menu(menu_items,
                                prompt,
                                preview_command=lambda x: x, #print traits to preview box
                                preview_title="Market prices",
                                preview_size=0.2)
    return menu_prompt(contract_menu)

#==========
def get_curr_market() -> None:
    """Simply prints out menu of market items so player can peruse them."""
    msg = "Market items at this waypoint. Select any to exit list."
    pick_item_from_market_menu(market_items_list,prompt=msg)

#==========
def buy_commodity() -> None:
    item = pick_item_from_market_menu(market_items_list,prompt="Pick an item to BUY from this market:")

    price = get_buy_price(item)
    free_capacity = ship_operator.cargo['capacity'] - ship_operator.cargo['units']

    cli_print(f"How many units of {item} would you like to BUY?")
    cli_print(f"(Price: {price:,} | Free cargo space: {free_capacity} units)")

    quantity = int(input("Type a number: "))

    cost = price * quantity

    msg = f"\nBuy {quantity} unit(s) of {item} for {cost:,} credits?"

    buy_option = "Yes, purchase."
    cancel_option = "No, cancel."
    menu = create_menu([buy_option,cancel_option],prompt=msg)
    choice = menu_prompt(menu)
    if choice == cancel_option:
        cli_clear()
        print_trade_menu_header()
        return None
    elif choice == buy_option:
        success = ship_operator.purchase(item,quantity)
        if success:
            cli_clear()
            print_trade_menu_header()
            cli_print("Purchase complete.")
        else:
            cli_print("Purchase could not be completed.\n")

#==========
def sell_commodity() -> None:
    cargo_items = [x['symbol'] for x in ship_operator.cargo['inventory']]
    available_items = [x for x in market_items_list if x['symbol'] in cargo_items]
    if len(available_items) == 0:
        cli_print("No items in cargo that can be sold at current market.")
        return None

    item = pick_item_from_market_menu(available_items, prompt="Pick an item to SELL to this market:")

    price = get_sell_price(item)
    cargo_record = [x for x in ship_operator.cargo['inventory'] if x['symbol'] == item][0]

    cli_print(f"How many units of {item} would you like to SELL?")
    cli_print(f"(Price: {price:,} | Quantity in cargo: {cargo_record['units']} units)")

    quantity = int(input("Type a number: "))

    cost = price * quantity

    msg = f"\nSell {quantity} unit(s) of {item} for {cost:,} credits?"

    sell_option = "Yes, sell."
    cancel_option = "No, cancel."
    menu = create_menu([sell_option,cancel_option],prompt=msg)
    choice = menu_prompt(menu)
    if choice == cancel_option:
        cli_clear()
        print_trade_menu_header()
        return None
    elif choice == sell_option:
        success = ship_operator.sell(item,quantity)
        if success:
            cli_clear()
            print_trade_menu_header()
            cli_print("Sale complete.")
        else:
            cli_print("Sale could not be completed.\n")

#==========
def get_profit_margins() -> None:
    """Allow players to get data on profit margins across all visited markets."""
    item_profit_opt = "Get best markets for a specific item"
    best_profits_opt = "Get best margins across all items"
    cancel_opt = "Cancel"

    menu = create_menu([item_profit_opt,best_profits_opt,cancel_opt],"Choose an option:")
    choice = menu_prompt(menu)

    if choice == cancel_opt:
        return None
    elif choice == best_profits_opt:
        return get_best_margins()
    elif choice == item_profit_opt:
        return get_item_margin()


#==========
def get_best_margins():
    """Show player data on the best profit margins - and where to find them - across all items."""
    best_margins = market.find_best_margins(limit = 3)
    #Creating formatted strings with margin details separated by '|' for menu preview:
    menu_items = []
    for item in best_margins:
        preview = format_margin_info_template(item)
        preview = preview.replace("|","\|") #For preview in menu, any normal bars must be escaped.
        menu_items.append(f"{item['item']}|{preview}")

    menu = create_menu(menu_items,
                        f"Best markets and margins across all items:",
                        preview_command=lambda x: x, #print traits to preview box
                        preview_title="",
                        preview_size=0.3)
    menu_prompt(menu)

#==========
def get_item_margin():
    """Show player data on where to find the best market prices for a particular item"""
    msg = "Pick an item to find optimal markets for:"
    item = pick_item_from_market_menu(market_items_list,prompt=msg)

    best_market = market.find_margin(item)

    menu_item = f"{item}|{format_margin_info_template(best_market)}"
    menu = create_menu([menu_item],
                                f"Best markets and margin for {item}:",
                                preview_command=lambda x: x, #print traits to preview box
                                preview_title="",
                                preview_size=0.3)
    menu_prompt(menu)
