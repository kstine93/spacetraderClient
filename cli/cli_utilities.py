import typer
from rich import print as rprint
from cli.art.ascii_art import *

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
def bootup_ui() -> None:
    cli_print(border_long_carat,"blue")
    cli_print(bootup_image,"yellow")
    cli_print(border_long_carat,"blue")
    cli_print(bootup_text)

#==========
def shutdown() -> None:
    cli_print("Goodbye captain")