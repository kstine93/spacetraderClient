from cli_utilities import cli_print
from art.str_formatting import format_contract_list
from src.contracts import Contracts

contracts = Contracts()

#==========
def list_contracts(color:str="chartreuse2") -> None:
    """Function to print out all contracts for a """
    data = contracts.list_all_contracts()
    cli_print(format_contract_list(data),color)