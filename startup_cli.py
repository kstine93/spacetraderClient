"""
This separate file before the game initializes is to allow the modification of the chosen player.
Can also be done manually (less fun) in the gameinfo.yaml file
"""
from PyInquirer import prompt
from src.base import SpaceTraderConfigSetup
import subprocess


#----------
def set_player() -> None:
    config_setup = SpaceTraderConfigSetup()
    callsigns = config_setup.get_all_callsigns()
    if len(callsigns) > 1:
        chosen_callsign = prompt_player_select(callsigns)
    else:
        chosen_callsign = callsigns[0]
    config_setup.set_new_current_agent(chosen_callsign)

#----------
def prompt_player_select(callsigns:list[str]) -> str:
    callsigns_list = [{"name":cs} for cs in callsigns]
    module_list_question = [
        {
            'type': 'list',
            'name': 'Players',
            'message': 'Please pick your player: ',
            'choices': callsigns_list,
        }
    ]
    answer_dict = prompt(module_list_question)
    return list(answer_dict.values())[0]

#----------
if __name__ == "__main__":
    set_player()
    subprocess.run(["python3","cli/main.py"])



