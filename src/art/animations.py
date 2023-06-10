from src.art.ascii_art import *
from time import sleep
import os
from IPython.display import clear_output

def animate(time:int,frames:list=[]):
    while time > 0:
        for item in frames:
            item = item.format(time) #For adding time if '{}' in frame
            os.system("clear") #For terminal
            clear_output(wait=True) #For Python notebooks
            print(item)
            sleep(1)
            time -= 1
    clear_output(wait=True)
    os.system("clear")


def animate_navigation(time:int):
    animate(time,frames=[nav_ship_1,nav_ship_2])
    print(arrived_ship)