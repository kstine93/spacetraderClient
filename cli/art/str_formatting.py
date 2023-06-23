"""Code to format data from the spacetrader client in ASCII (pretty printing"""

from src.utilities.basic_utilities import get_time_diff_UTC

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


