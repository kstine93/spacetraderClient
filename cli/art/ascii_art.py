# import rich
# import re

#NOTE: Attempted here to dynamically colorize ASCII, but it's gotten a bit too complicated.
# def rich_colorify(text:str,regex:str,color:str):
#     """Dynamically markup a string (or ASCII art) with color markup used by the 'rich' module"""
#     # text = re.sub(rf"{regex}","[yellow](1)[/yellow]",text)
#     text = re.sub(r"( \* )",r"[yellow]\g<1>[/yellow]",text)
#     rich.print(text)

border_long_carat =  """<><><><><><><><><><><><><><><><><><><><><><><><><><><><><>"""
border_med_carat  =  """<><><><><><><><><><><><><><><><><><><><><><><>"""
border_med_equals =  """=============================================="""
border_med_dash   =  """----------------------------------------------"""


border_main_menu  =  """================{ MAIN MENU }================"""
border_cmd_menu   =  """><><><><><><><><><><><><> COMMAND SHIP <><><><><><><><><><><><><"""
border_nav_menu  =   """------------------------ NAVIGATE SHIP ------------------------"""
border_mine_menu  =  """~~~~~~~~~~~~~~~~~~~~~~~~ MINE RESOURCES ~~~~~~~~~~~~~~~~~~~~~~~~"""
border_trade_menu  =  """____________________________ TRADE ____________________________"""

border_module_section =   """============= MODULES ============="""
border_mounts_section =   """============== MOUNTS =============="""
border_crew_section =     """=============== CREW ==============="""

border_menu_item =  """============================="""


bootup_image="""
   _____      .            _______       .    _
  / ____|         `  *    |__   __|          | |   '   .
 | (___  _ __   __ _  ___ ___| |_ __ __ _  __| | ___ _ __
  \___ \| '_ \ / _` |/ __/ _ \ | '__/ _` |/ _` |/ _ \ '__|
  ____) | |_) | (_| | (_|  __/ | | | (_| | (_| |  __/ |
 |_____/| .__/ \__,_|\___\___|_|_|  \__,_|\__,_|\___|_|
        | |      '                        .
    '   |_|    .             '        *              '
"""


#===================

nav_ship_1 = """
                       Navigating..
|          *          .                      `           |
|`     .           ____      '       .               '   |
|               -~-)___)>        .              *        |
|        '      ___\_ \______________     '              |
|    o       *    \_  o  o  o  o ~~ \_\_        .        |
|               .   \__._  .____[]_.___/               ` |
|             `     -~-)___)>            .               |
|  '                     .        *                o     |
|    .        `    ,                   `               . |
                      Time left: {}s
"""

nav_ship_2 = """
                       Navigating..
|         *          .                      `            |
|     .            ____     '        .              '    |
|             . ~-~)___)>       .              *        .|
|     '         ___\_ \______________    '               |
|   o      *      \_  o  o  o  o ~~ \_\_      .          |
|             .     \__._  .____[]_.___/              `  |
|         `         ~-~)___)>           .                |
| '                     .         *                o     |
|    .       `    ,                   `             .    |
                      Time left: {}s
"""

arrived_ship = """
                   Navigation complete
| ,   _    .          .                        | '       |
|    (_)           ____              *         .    o    |
|             .   @)___)>    .                  \        |
|      ___      ___\_ \______________    '       '.   '  |
|   * /  .\       \_  o  o  o  o ~~ \_\_      .    `.    |
|    | o   |  .     \__._  .____[]_.___/              ` .|
|     \___/           @)___)>           .       _        |
|   o             *     .                      (_)       |
|            `                  `                   *    |
                  Arrived at destination
"""