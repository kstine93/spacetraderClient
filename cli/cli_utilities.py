import typer
from os import system
from rich import print as rprint
from art.ascii_art import *
from simple_term_menu import TerminalMenu

#==========
def cli_clear() -> None:
    system('clear')

#==========
def cli_print(string:str,color:str|None=None) -> None:
    """Simple wrapper for all printing to terminal. Attempts to use colored output."""
    try:
        if color:
            rprint(f"[{color}]{string}[/{color}]")
        else:
            typer.echo(string)
    except:
        typer.echo(string)

#==========
def create_menu(menu_items:list[str],prompt:str='Choose your next action, Captain.',**kwargs) -> TerminalMenu:
    options = ["entry 1", "entry 2", "entry 3"]
    terminal_menu = TerminalMenu(menu_items,
                                 title=prompt,
                                 menu_cursor_style=("fg_green","bold"),
                                 menu_highlight_style=None,
                                 menu_cursor="-> "
                                )
    return terminal_menu

#==========
def use_menu(menu_dict:dict,**kwargs):
    menu = create_menu(list(menu_dict.keys()),**kwargs)
    cmd = menu_prompt(menu)
    command_switch(cmd,menu_dict)

#==========
def menu_prompt(menu:TerminalMenu) -> str:
    menu.show()
    return menu.chosen_menu_entry

#==========
def command_prompt(prompt:str="Use 'list' or 'menu' to get help. '<-back' for last menu.") -> str:
    cli_print(prompt)
    return typer.prompt("=")

#==========
def command_loop(cmd_list:dict,prompt:str|None=None,sep:str=border_med_equals,color:str="blue") -> None:
    while True:
        command = command_prompt(prompt) if prompt else command_prompt()
        if command in ["exit","<-back"]:
            break
        try:
            command_switch(command,cmd_list)
            cli_print(sep,color)
        except SystemExit as e:
            if str(e) != "0":
                typer.echo(f"Error: {e}")

#==========
def command_switch(cmd:str,cmd_map:dict) -> None:
    if cmd in cmd_map.keys():
        cmd_map[cmd].get('func')()
    else:
        cli_print(f"Command '{cmd}' not found","red")
        cli_print(border_med_equals,"red")

#==========
def list_cmds(menu_dict:dict):
    for (key,val) in menu_dict.items():
        cli_print(f"== '{key}' ==","orange1")
        cli_print(str(val['desc']))

