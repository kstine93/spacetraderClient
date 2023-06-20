import typer
from cli.cli_utilities import *
from cli.command_map import *

app = typer.Typer()

#----------
def main():
    bootup()
    while True:
        command = command_prompt()
        if command == "exit":
            shutdown()
            break
        try:
            command_switch(command)
        except SystemExit as e:
            if str(e) != "0":
                typer.echo(f"Error: {e}")


#----------
def command_prompt() -> str:
    cli_print("Use 'list' to get list of possible commands or use 'menu'.")
    return typer.prompt("=")


#----------
def command_switch(cmd) -> None:
    if cmd in command_map.keys():
        command_map[cmd].get('func')()
    else:
        cli_print(f"Command '{cmd}' not found","red")
        cli_print(border_med_equals,"red")



#----------
#----------
if __name__ == "__main__":
    typer.run(main)