"""Code to format data from the spacetrader client in ASCII (pretty printing"""

from src.utilities.basic_utilities import get_time_diff_UTC,dedup_list

def remove_list_formatting(user_list:str):
    user_list = str(user_list)[1:-1]
    return user_list.replace("'","")

#---------------
#-- CONTRACTS --
#---------------
contract_template = """\
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
~~~~~~~~~~~~~~ CONTRACT ~~~~~~~~~~~~~~
-- ID: {contract_id}
--------------------------------------
-- Pay up front: {first_pay}
-- Pay on complete: {deliver_pay}
--------------------------------------
-- Type: {type}
-- Item: {item}
-- Quantity: {quantity_division}
--------------------------------------
-- Accepted: {accepted}
-- Time to accept: {accept_deadline}
-- Time to fulfill: {fulfill_deadline}
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