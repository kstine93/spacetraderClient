"""Code to format data from the spacetrader client in ASCII (pretty printing)"""

from src.utilities.basic_utilities import get_time_diff_UTC, dedup_list, halve_into_two_ints
from textwrap import fill

#------------------------
#-- GENERIC FORMATTING --
#------------------------
def remove_list_formatting(user_list:str):
    user_list = str(user_list)[1:-1]
    return user_list.replace("'","")

#---------------
def pad_string(string:str,target_len:int,pad_char:str=" ",prefix:bool=True,affix:bool=True) -> str:
    '''utility function to pad strings to make them a desired length. Used primarily for keeping
    ASCII art correct while still allowing string formatting.
    note that 'prefix' and 'affix' denote whether the padding should come before or after the string
    (or both if both are True).
    '''
    pre_str = ""
    aff_str = ""

    buffer_len = target_len - len(string)

    if prefix and affix:
        pre_len, aff_len = halve_into_two_ints(buffer_len)
        pre_str = pre_len * pad_char
        aff_str = aff_len * pad_char
    elif prefix:
        pre_str = buffer_len * pad_char
    elif affix:
        aff_str = buffer_len * pad_char

    return pre_str + string + aff_str

#---------------
def dict_to_formatted_string(obj:dict|list,
                             prefix:str=" | ",
                             indent:int=0,
                             keys_to_ignore:list[str]=[],
                             len_limit=70):
    """
    Function to custom format a dictionary as a string that can then be printed as an indented list
    """
    string = ""
    indent_add = 3
    indent_str = ' '

    if isinstance(obj,dict):
        for (key,val) in obj.items():
            if key in keys_to_ignore:
                continue
            curr_prefix = f"{prefix}{indent * indent_str}"
            #where value is not another nested object, just add "key: value" with no extra indents.
            if not isinstance(val,dict) and not isinstance(val,list):
                #If string will be longer than given len_limit, then split onto multiple lines
                string += fill(text=f"{key}: {val}",
                               width=len_limit,
                               initial_indent=curr_prefix,
                               subsequent_indent=curr_prefix + (indent_str * indent_add))
                string += "\n"
            else:
                string += f"{curr_prefix}{key}:\n"
                string += dict_to_formatted_string(val,prefix,indent + indent_add,keys_to_ignore)
    elif isinstance(obj,list):
        for elem in obj:
            string += dict_to_formatted_string(elem,prefix,indent,keys_to_ignore)
    else:
        curr_prefix = f"{prefix}{indent * indent_str}"
        #If string will be longer than given len_limit, then split onto multiple lines
        string += fill(text=obj,
             width=len_limit,
             initial_indent=curr_prefix,
             subsequent_indent=curr_prefix + (indent_str * indent_add))
        string += "\n"
    return string

#---------------
#-- CONTRACTS --
#---------------
contract_header = """============ CONTRACTS ============"""

contract_template = """\
 | > ID: {contract_id} <
 |
 | Destination: {dest_symbol}
 | Pay up front: {first_pay}
 | Pay on complete: {deliver_pay}
 |
 | Type: {type}
 | Item: {item}
 | Quantity: {quantity_division}
 |
 | Accepted: {accepted}
 | Time to accept: {accept_deadline}
 | Time to fulfill: {fulfill_deadline}
 |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\
"""

#---------------
def format_contract_list(contract_list:list[dict]) -> str:
    string = contract_header
    for contract in contract_list[0].values():
        string += "\n"
        string += format_contract_template(contract)
    return string

#---------------
def format_contract_template(contract:dict) -> str:
    """Format the contract template with data returned from the 'Contracts' class"""
    terms = contract['terms']
    deliver = terms['deliver'][0]

    first_pay = terms["payment"]["onAccepted"]
    deliver_pay = terms["payment"]["onFulfilled"]

    quantity_division = f'{deliver["unitsFulfilled"]} / {deliver["unitsRequired"]}'
    accepted = "YES" if contract["accepted"] else "NO"

    accept_timedelta = get_time_diff_UTC(contract["deadlineToAccept"])
    fulfill_timedelta = get_time_diff_UTC(terms["deadline"])

    format_dict = {
        "contract_id": contract["id"],
        "dest_symbol": deliver["destinationSymbol"],
        "first_pay": f'{first_pay:,}', #formatted with commas
        "deliver_pay": f'{deliver_pay:,}', #formatted with commas
        "type": contract["type"],
        "item": deliver["tradeSymbol"],
        "quantity_division": quantity_division,
        "accepted": accepted,
        "accept_deadline": str(accept_timedelta),
        "fulfill_deadline": str(fulfill_timedelta)
    }

    return contract_template.format(**format_dict)

#---------------
#-- WAYPOINTS --
#---------------

#NOTE: the bar | in this template signals to simple_term_menu module that what comes after the bar
#should be sent to the 'preview' window instead.
waypoint_template = """{num}. {symbol} ({type}) | {trait_list}"""

#---------------
def format_waypoint_template(number:int,waypoint:dict) -> str:
    """Format the waypoint template with data returned from the current system
    Designed to be part of a list of waypoints with 'number' giving index in list"""
    format_dict = {
    "num": number,
    "symbol": waypoint["symbol"],
    "type": waypoint["type"],
    "trait_list": "(Traits unknown - waypoint not yet scanned)"
    }
    if 'traits' in waypoint.keys():
        format_dict['trait_list'] = remove_list_formatting(waypoint['traits'])
    return waypoint_template.format(**format_dict)

#-------------
#-- SURVEYS --
#-------------
survey_template = """\
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~ SURVEY ~~~~~~~~~~~~~~
Location: {symbol}
---------------------------------
Size: {size}
---------------------------------
Deposits:
{deposits}
"""

#---------------
def format_survey_template(survey:dict) -> str:
    """Format the survey template with data from the collected survey data."""
    dep_list = [item['symbol'] for item in survey['deposits']]
    dep_list = dedup_list(dep_list)
    dep_list = [f"> {dep}" for dep in dep_list] #Prefixing strings

    format_dict = {
    "symbol": survey["symbol"],
    "size": survey["size"],
    "deposits": "\n".join(dep_list)
    }
    return survey_template.format(**format_dict)


#---------------
surveyMenu_template = """{num}. {signature} | (Size: {size})\n{deposits}"""

#---------------
def format_surveyMenu_template(number:int,survey:dict) -> str:
    """Format the survey template with data from the collected survey data."""
    dep_list = [item['symbol'] for item in survey['deposits']]
    dep_list = dedup_list(dep_list)
    dep_list = [f"- {dep}" for dep in dep_list] #Prefixing strings

    format_dict = {
    "num": number,
    "signature": survey["signature"],
    "size": survey["size"],
    "deposits": "\n".join(dep_list)
    }
    return surveyMenu_template.format(**format_dict)

#----------------------------
#-- HEADS-UP DISPLAY (HUD) --
#----------------------------
'''
// concept //
================================================================
 | [   Mode:   ]   `    '     . *          `  [   System:   ] |
 | [  CRUISE   ]   '   ____   .    '    *     [ X1-YX2 (10) ] |
 | .        *     . ~-~)___)>       .     `         *       . |
 |     '   .          __\_ \_______________   '  .            |
 |   o       *    '    \_  o  o  o  o ~~ \_\_      .    '     |
 |              .    `   \__._  .____[]_.___/         *    `  |
 |         `        .    ~-~)___)>        '    .              |
 | [   Fuel:   ]         .         *          `         o     |
 | [ 1200/1200 ]   ,              .        `             .    |
================================================================
 | Ship: AMBROSIUS-RITZ-1
 | Waypoint: X1-KS52-23717D
 | Credits: 15.000.000
 ============ SHIP INFO ============
 | symbol: FRAME_FRIGATE
 | description: A medium-sized, multi-purpose spacecraft, often used
 | for combat, transport, or support operations.
 | moduleSlots: 8
 | mountingPoints: 5
 | fuelCapacity: 1200
 | condition: 100
 | requirements:
 |    power: 8
 |    crew: 25
 ============= REACTOR =============
 | symbol: REACTOR_FISSION_I
 | description: A basic fission power reactor, used to generate electricity
 | from nuclear fission reactions.
 | condition: 100
 | powerOutput: 31
 | requirements:
 |    crew: 8
 ========== CARGO [59/60] ==========
 | PRECIOUS_STONES = 5
 | IRON_ORE = 24
 | AMMONIA_ICE = 30
 =============== CREW ===============
 | capacity: 59 / 80
 | required: 59
 | rotation: STRICT
 | morale: 100
 | wages: 0
 ============== MOUNTS ==============
 | << MOUNT_SENSOR_ARRAY_I >>
 | strength: 1
 | requirements:
 |    power: 1
 |    crew: 0
 | description: A basic sensor array that improves a ship's ability
 | to detect and track other objects in space.
 |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 | << MOUNT_SURVEYOR_I >>
 | strength: 1
 | crew: 0
 | power: 1
 | description: A basic mining laser that can be used to extract
 | valuable minerals from asteroids and other space objects.
 | deposits:
 |    'QUARTZ_SAND',
 |    'SILICON_CRYSTALS',
 |    'PRECIOUS_STONES',
 |    'ICE_WATER',
 |    'AMMONIA_ICE',
 |    'IRON_ORE',
 |    'COPPER_ORE',
 |    'SILVER_ORE',
 |    'ALUMINUM_ORE',
 |    'GOLD_ORE',
 |    'PLATINUM_ORE'
 ============= MODULES =============
 | ** MODULE_MINERAL_PROCESSOR_I **
 | slots: 1
 | crew: 0
 | power: 1
 | description: Crushes and processes extracted minerals and ores
 | into their component parts, filters out impurities, and
 | containerizes them into raw storage units.
 |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
 | ** MODULE_MINERAL_PROCESSOR_II **
 | slots: 1
 | crew: 1
 | power: 3
 | description: Crushes and processes extracted minerals and ores
 | into their component parts, filters out impurities, and
 | containerizes them into raw storage units.

'''

#---------------
base_hud_template = """\
================================================================
 | [   Mode:   ]   `    '     . *          `  [   System:   ] |
 | [{flightMode}]   '   ____   .    '    *     [{system}] |
 | .        *     . ~-~)___)>       .     `         *       . |
 |     '   .          __\_ \_______________   '  .            |
 |   o       *    '    \_  o  o  o  o ~~ \_\_      .    '     |
 |              .    `   \__._  .____[]_.___/         *    `  |
 |         `        .    ~-~)___)>        '    .              |
 | [   Fuel:   ]         .         *          `         o     |
 | [{fuel}]   ,              .        `             .    |
================================================================\
"""
#---------------
#How many characters should be inputted for the placeholder values so that the ASCII
#art is correctly rendered (spacing matters with ASCII)
base_hud_str_lens = {
    'flightMode':11,
    'system':13,
    'fuel':11
}


#---------------
def format_base_hud_template(flightMode:str,system:dict,fuel:dict) -> str:
    """Format the HUD template with data from the ship's information"""

    num_waypoints = len(system['waypoints'])
    sys_str = system['symbol'] + " (" + str(num_waypoints) + ")"

    fuel_str = str(fuel['current']) + "/" + str(fuel['capacity'])

    format_dict = {
        "flightMode": pad_string(flightMode,base_hud_str_lens['flightMode']),
        "system": pad_string(sys_str,base_hud_str_lens['system']),
        "fuel": pad_string(fuel_str,base_hud_str_lens["fuel"])
    }
    return base_hud_template.format(**format_dict)

#------------------------
#-- SHIP INFO: GENERAL --
#------------------------
ship_info_template = '''\
============ SHIP INFO ============
 | Ship: {ship_name}
 | Waypoint: {wp_symbol}
 | Credits: {credits}\
'''

#---------------
def format_ship_info_template(ship_name:str,waypoint:dict,credits:int) -> str:
    format_dict = {
        "ship_name": ship_name,
        "wp_symbol": waypoint['symbol'],
        "credits": f'{credits:,}', #formatted with commas
    }
    return ship_info_template.format(**format_dict)

#----------------------
#-- SHIP INFO: CARGO --
#----------------------
cargo_info_template = '''\
===={cargo_header}====
{formatted_cargo_list}\
'''

cargo_info_str_lens = {
    'cargo_header':27,
}

#---------------
def format_cargo_info_template(cargo:dict) -> str:
    header_str = f" CARGO [{cargo['units']}/{cargo['capacity']}] "

    cargo_dict = {item['symbol']:item['units'] for item in cargo['inventory']}
    cargo_list = [f" | {key} = {val}" for (key,val) in cargo_dict.items()]
    format_dict = {
        "cargo_header": pad_string(header_str,cargo_info_str_lens['cargo_header'],pad_char="="),
        "formatted_cargo_list": "\n".join(cargo_list)
    }
    return cargo_info_template.format(**format_dict)

#-----------------------
#-- SHIP INFO: MOUNTS --
#-----------------------
ship_mount_info_header = """============= MOUNTS ============="""

#---------------
def format_ship_mount_info_template(mounts:list[dict]) -> str:
    string = f"{ship_mount_info_header}\n"
    len_limit = 64 #maximum line width for information printed out
    for mnt in mounts:
        title = mnt.pop('symbol')
        string += f" | > {title} <\n"
        string += dict_to_formatted_string(mnt,keys_to_ignore=['name'],len_limit=len_limit)
        string +=  " |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
    return string


