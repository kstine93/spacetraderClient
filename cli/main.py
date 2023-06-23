import typer
from PyInquirer import prompt
from cli.cli_utilities import *
from src.contracts import *
from src.ships import *
from cli.command import *
from cli.art.str_formatting import format_contract_template

#==========
app = typer.Typer()
contracts = Contracts()
ships = Ships()

#==========
def main_menu_loop() -> None:
    bootup()
    prompt = "Use 'list' or 'menu' to get help. 'exit' to stop playing."
    command_loop(main_menu,prompt)
    shutdown()

#==========
def bootup() -> None:
    cli_print(border_long_carat,"blue")
    cli_print(bootup_image,"yellow")
    cli_print(border_long_carat,"blue")
    cli_print(bootup_text)

#==========
def shutdown() -> None:
    cli_print("Goodbye captain")

#==========
main_menu = {
    "contracts": {
        "func": lambda: main_list_contracts(),
        "desc": "List all active contracts."
    },
    "command": {
        "func": lambda: command_ship(),
        "desc": "Command one of your ships - play the game!"
    },
    "explore": {
        "func": lambda: explore_systems(),
        "desc": "Learn more about the galaxy you're playing in."
    },
    "list": {
        "func": lambda: list_cmds(main_menu),
        "desc": "List the commands in this menu."
    },
    "menu": {
        "func": lambda: use_menu(main_menu),
        "desc": "Provide interactive menu of commands."
    }
}

#==========
def main_list_contracts() -> None:
    data = contracts.list_all_contracts()
    for contract in data.values():
        cli_print(format_contract_template(contract),"chartreuse2")

#==========
def explore_systems() -> None:
    print("Not yet implemented - sorry!")

#==========
def command_ship() -> None:
    data = ships.list_all_ships()
    ship_list = list(data.keys())
    if len(ship_list) > 1:
        ship_menu = create_menu(ship_list,prompt="Choose a ship to command, Captain:")
        chosen_ship = menu_prompt(ship_menu)
    else:
        chosen_ship = ship_list[0]
    startup_ship_command(chosen_ship)




#==========
#==========
if __name__ == "__main__":
    typer.run(main_menu_loop)