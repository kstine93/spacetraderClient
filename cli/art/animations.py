from cli.art.ascii_art import *
from time import sleep
import os

def animate(time:int,frames:list=[]):
    while time > 0:
        for item in frames:
            item = item.format(time) #For adding time if '{}' in frame
            os.system("clear") #For terminal
            print(item)
            sleep(1)
            time -= 1
    os.system("clear")


def animate_navigation(time:int):
    animate(time,frames=[nav_ship_1,nav_ship_2])
    print(arrived_ship)


if __name__ == "__main__":
    animate_navigation(5)