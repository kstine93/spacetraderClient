"""Code to format data from the spacetrader client in ASCII (pretty printing)"""

from src.utilities.basic_utilities import get_time_diff_UTC, dedup_list, halve_into_two_ints

#---------------
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
#-- CONTRACTS --
#---------------
contract_template = """\
| ID: {contract_id}
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
|~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\
"""

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

#----------------------
#-- HEADS-UP DISPLAY --
#----------------------
'''
// concept //
___________________________________________________________________
 \      |/                 [STEALTH MODE]                \|      /
  \     |`                 .                      *       |     /
   \    |         *                    o                  |    /
    \   | .                   *                         . |   /
     \  |               `                     '           |  /
      \ |       .        o        '                    *  | /
       \|\_______________________________________________/|/
       /  [   System:   ] o  __      __  +  [   Fuel:   ]  \
      /   [ X1-KS52 (8) ] +  \_\____/_/  o  [ 1200/1200 ]   \
  ___/___________________________||__________________________\___
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
 | 'deposits':
 | 'QUARTZ_SAND',
 | 'SILICON_CRYSTALS',
 | 'PRECIOUS_STONES',
 | 'ICE_WATER',
 | 'AMMONIA_ICE',
 | 'IRON_ORE',
 | 'COPPER_ORE',
 | 'SILVER_ORE',
 | 'ALUMINUM_ORE',
 | 'GOLD_ORE',
 | 'PLATINUM_ORE'
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
 ============= REACTOR =============
 |
 |

'''

#---------------
base_hud_template = """\
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  |    |/               {flightMode}              \|    |
  |    |`                 .                      *       |    |
  |    |         *                    o                  |    |
   \   | .                   *                         . |   /
    \  |               `                     '           |  /
     \ |       .        o        '                    *  | /
      \|\_______________________________________________/|/
      /  [   System:   ] o  __      __  +  [   Fuel:   ]  \\
     /   [{system}] +  \_\____/_/  o  [{fuel}]   \\
  __/___________________________||__________________________\__
  -------------------------------------------------------------\
"""
#---------------
#How many characters should be inputted for the placeholder values so that the ASCII
#art is correctly rendered (spacing matters with ASCII)
base_hud_str_lens = {
    'flightMode':18,
    'system':13,
    'fuel':11
}

#---------------
def format_base_hud_template(flightMode:str,system:dict,fuel:dict) -> str:
    """Format the HUD template with data from the ship's information"""
    flight_mode_str = "[" + flightMode + " MODE]"

    num_waypoints = len(system['waypoints'])
    sys_str = system['symbol'] + " (" + str(num_waypoints) + ")"

    fuel_str = str(fuel['current']) + "/" + str(fuel['capacity'])

    format_dict = {
        "flightMode": pad_string(flight_mode_str,base_hud_str_lens['flightMode']),
        "system": pad_string(sys_str,base_hud_str_lens['system']),
        "fuel": pad_string(fuel_str,base_hud_str_lens["fuel"])
    }
    return base_hud_template.format(**format_dict)