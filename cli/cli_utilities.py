import typer
from os import system
from rich import print as rprint
from art.ascii_art import *
from simple_term_menu import TerminalMenu
from typing import Callable

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
def create_menu(menu_items:list[str],prompt:str='Choose your next action, Captain.',**kwargs) -> TerminalMenu:
    terminal_menu = TerminalMenu(menu_items,
                                 title=prompt,
                                 menu_cursor_style=("fg_green","bold"),
                                 menu_highlight_style=None,
                                 menu_cursor="-> ",
                                 **kwargs
                                )
    return terminal_menu

#==========
def use_menu(menu_dict:dict,**kwargs):
    menu = create_menu(list(menu_dict.keys()),**kwargs)
    cmd = menu_prompt(menu)
    command_switch(cmd,menu_dict)

#==========
def menu_prompt(menu:TerminalMenu,index:bool=False) -> str:
    menu.show()
    return menu.chosen_menu_index if index else menu.chosen_menu_entry

#==========
def command_prompt(prompt:str="Use 'list' or 'menu' to get help. '<-back' for last menu.") -> str:
    cli_print(prompt)
    return typer.prompt("=")


#==========
def print_generic_header() -> str:
    cli_print(border_med_equals,"white")

#==========
def command_loop(cmd_list:dict,prompt:str|None=None,loop_func:Callable=print_generic_header) -> bool:
    """Generic function to loop indefinitely while processing user commands. The given cmd_list
    provides a standardized mapping of strings with commands (e.g., "{'nav':Navigate_Ship()}").
    Returns a bool flag only to show whether the command was given to exit the game (True).

    Note that the 'loop_func' is to allow the user to have a function called BEFORE the results of
    commands are processed. A basic use of this is to print a 'header' which appears
    above prompts (e.g., a heads-up display)
    """
    while True:
        command = command_prompt(prompt) if prompt else command_prompt()
        if command == "<-back": #Return to previous command loop
            break
        if command == "exit": #Return flag showing that all parent command loops should end
            return True
        try:
            cli_clear()
            loop_func()
            res = command_switch(command,cmd_list)
            if res == True: #If response is True, it means an exit command has been given.
                return True
        except SystemExit as e:
            if str(e) != "0":
                typer.echo(f"Error: {e}")
    return False

#==========
def command_switch(cmd:str,cmd_map:dict) -> bool | None:
    if cmd in cmd_map.keys():
        return cmd_map[cmd].get('func')()
    else:
        cli_print(f"Command '{cmd}' not found","red")
        cli_print(border_med_equals,"red")
    return False

#==========
def list_cmds(menu_dict:dict):
    # cli_clear()
    for (key,val) in menu_dict.items():
        cli_print(f"== '{key}' ==","orange1")
        cli_print(str(val['desc']))
