"""Code to format data from the spacetrader client in ASCII (pretty printing)"""

from src.utilities.basic_utilities import get_time_diff_UTC, dedup_list
from .str_utilities import *

# ---------------
# -- CONTRACTS --
# ---------------
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


# ---------------
def format_contract_list(contract_list: list[dict]) -> str:
    string = contract_header
    for contract in contract_list[0].values():
        string += "\n"
        string += format_contract_template(contract)
    return string


# ---------------
def format_contract_template(contract: dict) -> str:
    """Format the contract template with data returned from the 'Contracts' class"""
    terms = contract["terms"]
    deliver = terms["deliver"][0]

    first_pay = terms["payment"]["onAccepted"]
    deliver_pay = terms["payment"]["onFulfilled"]

    quantity_division = f'{deliver["unitsFulfilled"]} / {deliver["unitsRequired"]}'
    accepted = "YES" if contract["accepted"] else "NO"

    accept_timedelta = get_time_diff_UTC(contract["deadlineToAccept"])
    fulfill_timedelta = get_time_diff_UTC(terms["deadline"])

    format_dict = {
        "contract_id": contract["id"],
        "dest_symbol": deliver["destinationSymbol"],
        "first_pay": f"{first_pay:,}",  # formatted with commas
        "deliver_pay": f"{deliver_pay:,}",  # formatted with commas
        "type": contract["type"],
        "item": deliver["tradeSymbol"],
        "quantity_division": quantity_division,
        "accepted": accepted,
        "accept_deadline": str(accept_timedelta),
        "fulfill_deadline": str(fulfill_timedelta),
    }

    return contract_template.format(**format_dict)


# ---------------
# -- WAYPOINTS --
# ---------------

# NOTE: the bar | in this template signals to simple_term_menu module that what comes after the bar
# should be sent to the 'preview' window instead.
waypoint_template = """{num}. {symbol} ({type}) | {trait_list}"""


# ---------------
def format_waypoint_template(number: int, waypoint: dict) -> str:
    """Format the waypoint template with data returned from the current system
    Designed to be part of a list of waypoints with 'number' giving index in list"""
    format_dict = {
        "num": number,
        "symbol": waypoint["symbol"],
        "type": waypoint["type"],
        "trait_list": "(Traits unknown - waypoint not yet scanned)",
    }
    if "traits" in waypoint.keys():
        format_dict["trait_list"] = remove_list_formatting(waypoint["traits"])
    return waypoint_template.format(**format_dict)


# -------------
# -- SURVEYS --
# -------------
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


# ---------------
def format_survey_template(survey: dict) -> str:
    """Format the survey template with data from the collected survey data."""
    dep_list = [item["symbol"] for item in survey["deposits"]]
    dep_list = dedup_list(dep_list)
    dep_list = [f"> {dep}" for dep in dep_list]  # Prefixing strings

    format_dict = {
        "symbol": survey["symbol"],
        "size": survey["size"],
        "deposits": "\n".join(dep_list),
    }
    return survey_template.format(**format_dict)


# ---------------
surveyMenu_template = """{num}. {signature} | (Size: {size})\n{deposits}"""


# ---------------
def format_surveyMenu_template(number: int, survey: dict) -> str:
    """Format the survey template with data from the collected survey data."""
    dep_list = [item["symbol"] for item in survey["deposits"]]
    dep_list = dedup_list(dep_list)
    dep_list = [f"- {dep}" for dep in dep_list]  # Prefixing strings

    format_dict = {
        "num": number,
        "signature": survey["signature"],
        "size": survey["size"],
        "deposits": "\n".join(dep_list),
    }
    return surveyMenu_template.format(**format_dict)


# ----------------------------
# -- HEADS-UP DISPLAY (HUD) --
# ----------------------------
"""
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

"""

# ---------------
base_hud_template = """\
=={spaceshipName}==
 | [   Mode:   ]   `    '     . *          ` [    System:   ] |
 | [{flightMode}]  '   ____   .    '    *     [{system}] |
 | .        *    . ~-~)___)>       .     `         *        . |
 |     '   .         __\_ \_______________   '   .            |
 |   o       *   '    \_  o  o  o  o ~~ \_\_      .     '     |
 |              .   `   \__._  .____[]_.___/         *     `  |
 |         `        .   ~-~)___)>        '    .               |
 | [   Fuel:   ]         .         *         [   Credits:   ] |
 | [{fuel}]   ,              .        ` [{credits}] |
=={currentLocation}==
````````````````````````````````````````````````````````````````\
"""
# ---------------
# How many characters should be inputted for the placeholder values so that the ASCII
# art is correctly rendered (spacing matters with ASCII)
base_hud_str_lens = {
    "flightMode": 11,
    "system": 14,
    "fuel": 11,
    "credits":14,
    "currentLocation":60,
    "spaceshipName":60
}

# ---------------
def format_base_hud_template(shipName: str,
                             flightMode: str,
                             system: dict,
                             waypoint: dict,
                             fuel: dict,
                             credits: int) -> str:
    """Format the HUD template with data from the ship's information"""

    spaceship_str = f" {shipName} "

    num_waypoints = len(system["waypoints"])
    sys_str = system["symbol"] + " (" + str(num_waypoints) + ")"

    fuel_str = str(fuel["current"]) + "/" + str(fuel["capacity"])

    credits_str = f"{credits:,}"

    waypoint_str = f" Location: {waypoint['symbol']} ({waypoint['type']}) "

    format_dict = {
        "spaceshipName": pad_string(spaceship_str, base_hud_str_lens["spaceshipName"],pad_char="="),
        "flightMode": pad_string(flightMode, base_hud_str_lens["flightMode"]),
        "system": pad_string(sys_str, base_hud_str_lens["system"]),
        "fuel": pad_string(fuel_str, base_hud_str_lens["fuel"]),
        "credits": pad_string(credits_str, base_hud_str_lens["credits"]),
        "currentLocation":pad_string(waypoint_str,base_hud_str_lens["currentLocation"],pad_char="=")
    }
    return base_hud_template.format(**format_dict)

# ----------------------
# -- SHIP INFO: FRAME --
# ----------------------
ship_frame_header = """=========== FRAME INFO ==========="""


# ---------------
def format_frame_info_template(frame_info: dict) -> str:
    string = f"{ship_frame_header}\n"
    len_limit = 64  # maximum line width for information printed out
    string += dict_to_formatted_string(frame_info,keys_to_ignore=['name'],len_limit=len_limit)
    return string


# ------------------------
# -- SHIP INFO: REACTOR --
# ------------------------
ship_reactor_header = """========== REACTOR INFO =========="""


# ---------------
def format_reactor_info_template(reactor_info: dict) -> str:
    string = f"{ship_reactor_header}\n"
    len_limit = 64  # maximum line width for information printed out
    string += dict_to_formatted_string(reactor_info,keys_to_ignore=['name'],len_limit=len_limit)
    return string


# -----------------------
# -- SHIP INFO: ENGINE --
# -----------------------
ship_engine_header = """=========== ENGINE INFO ==========="""


# ---------------
def format_engine_info_template(engine_info: dict) -> str:
    string = f"{ship_engine_header}\n"
    len_limit = 64  # maximum line width for information printed out
    string += dict_to_formatted_string(engine_info,keys_to_ignore=['name'],len_limit=len_limit)
    return string


# ----------------------
# -- SHIP INFO: CARGO --
# ----------------------
cargo_info_template = """\
===={cargo_header}====
{formatted_cargo_list}\
"""

cargo_info_str_lens = {
    "cargo_header": 27,
}


# ---------------
def format_cargo_info_template(cargo: dict) -> str:
    header_str = f" CARGO [{cargo['units']}/{cargo['capacity']}] "
    cargo_dict = {item["symbol"]: item["units"] for item in cargo["inventory"]}
    if len(cargo_dict.items()) < 1:
        cargo_list_str = " | (No cargo in ship)"
    else:
        cargo_list = [f" | {key} = {val}" for (key, val) in cargo_dict.items()]
        cargo_list_str = "\n".join(cargo_list)

    format_dict = {
        "cargo_header": pad_string(
            header_str, cargo_info_str_lens["cargo_header"], pad_char="="
        ),
        "formatted_cargo_list": cargo_list_str,
    }
    return cargo_info_template.format(**format_dict)


# -----------------------
# -- SHIP INFO: MOUNTS --
# -----------------------
ship_mount_info_header = """>>>>>>> MOUNTS {} >>>>>>>"""

# ---------------
mount_info_str_lens = {
    "mount_header": 34,
}

# ---------------
def format_ship_mount_info_template(mounts: list[dict],mountingPoints:int) -> str:
    #Format header with # of occupied mount slots over total capacity
    header = ship_mount_info_header.format(f"[{len(mounts)}/{mountingPoints}]")
    string = pad_string(header,mount_info_str_lens['mount_header'],pad_char=">")

    len_limit = 64  # maximum line width for information printed out
    for mnt in mounts:
        title = mnt.pop("symbol")
        string += f"\n | > {title} <\n"
        string += dict_to_formatted_string(
            mnt, keys_to_ignore=["name"], len_limit=len_limit
        )
        string += " |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    return string


# ------------------------
# -- SHIP INFO: MODULES --
# ------------------------
ship_modules_info_header = """******* MODULES {} *******"""

modules_info_str_lens = {
    'module_header':34
}

# ---------------
def format_ship_modules_info_template(modules: list[dict],moduleSlots:int) -> str:
    #Format header with # of occupied mount slots over total capacity
    header = ship_modules_info_header.format(f"[{len(modules)}/{moduleSlots}]")
    string = pad_string(header,modules_info_str_lens['module_header'],pad_char="*")
    len_limit = 64  # maximum line width for information printed out
    # for mod in modules:
    for mod in modules:
        title = mod.pop("symbol")
        string += f"\n | ** {title} **\n"
        string += dict_to_formatted_string(
            mod, keys_to_ignore=["name"], len_limit=len_limit
        )
        string += " |~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    return string


# ---------------------
# -- SHIP INFO: CREW --
# ---------------------
crew_info_template = """\
===={crew_header}====
 | Required: {required}
 | Rotation: {rotation}
 | Morale: {morale}
 | Wages: {wages}\
"""

crew_info_str_lens = {
    "crew_header": 27,
}


# ---------------
def format_crew_info_template(crew: dict) -> str:
    header_str = f" CREW [{crew['current']}/{crew['capacity']}] "

    format_dict = {
        "crew_header": pad_string(
            header_str, crew_info_str_lens["crew_header"], pad_char="="
        ),
        "required": crew["required"],
        "rotation": crew["rotation"],
        "morale": crew["morale"],
        "wages": crew["wages"],
    }
    return crew_info_template.format(**format_dict)
