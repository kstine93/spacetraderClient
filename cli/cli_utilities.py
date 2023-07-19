import typer
from os import system
from rich import print as rprint
from art.ascii_art import *
from simple_term_menu import TerminalMenu
from typing import Callable
from enum import Enum

#==========
class CliCommand(Enum):
    #Commands that are used internally to the command structures of the CLI
    exit = 1
    back = 2

#==========
def cli_clear() -> None:
    system('clear')

#==========
def cli_print(string:str,color:str|None=None) -> None:
    """Simple wrapper for all printing to terminal. Attempts to use colored output."""
    try:
        if color:
            #color list: https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
            rprint(f"[{color}]{string}[/{color}]")
        else:
            typer.echo(string)
    except:
        typer.echo(string)

#==========
def create_menu(menu_items:list[str],
                prompt:str='Choose your next action, Captain.',
                **kwargs) -> TerminalMenu:
    terminal_menu = TerminalMenu(menu_items,
                                 title=prompt,
                                 menu_cursor_style=("fg_green","bold"),
                                 menu_highlight_style=None,
                                 menu_cursor="-> ",
                                 **kwargs
                                )
    return terminal_menu

#==========
def use_menu(menu_dict:dict,**kwargs) -> CliCommand | None:
    menu = create_menu(list(menu_dict.keys()),**kwargs)
    cmd = menu_prompt(menu)
    return command_switch(cmd,menu_dict)

#==========
def menu_prompt(menu:TerminalMenu,index:bool=False) -> str:
    menu.show()
    return menu.chosen_menu_index if index else menu.chosen_menu_entry

#==========
def print_generic_header() -> str:
    cli_print(border_med_equals,"white")

#==========
def command_loop(cmd_list:dict,
                 prompt:str|None=None,
                 loop_func:Callable=print_generic_header) -> CliCommand | None:
    """Generic function to loop indefinitely while processing user commands. The given cmd_list
    provides a standardized mapping of strings with commands (e.g., "{'nav':Navigate_Ship()}").
    Returns a bool flag only to show whether the command was given to exit the game (True).

    Note that the 'loop_func' is to allow the user to have a function called BEFORE the results of
    commands are processed. A basic use of this is to print a 'header' which appears
    above prompts (e.g., a heads-up display)
    """
    while True:
        if prompt:
            cli_print(prompt)
        command = input("-> ")
        try:
            cli_clear()
            loop_func()
            res = command_switch(command,cmd_list)
            if res == "exit":
                return res
            if res == "back":
                break
        except SystemExit as e:
            if str(e) != "0":
                typer.echo(f"Error: {e}")
    return None

#==========
def command_switch(cmd:str,cmd_map:dict) -> CliCommand | None:
    if cmd in cmd_map.keys():
        return cmd_map[cmd].get('func')()
    else:
        cli_print(f"Command '{cmd}' not found","red")
        cli_print(border_med_equals,"red")
    return None

#==========
def list_cmds(menu_dict:dict) -> None:
    for (key,val) in menu_dict.items():
        cli_print(f"-> {key}","orange1")
        cli_print(str(val['desc']))
    cli_print(border_med_dash,"orange1")