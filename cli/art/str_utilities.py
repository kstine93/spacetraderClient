
"""Generic utility functions for formatting strings for pretty-printing"""

# ---------------
from src.utilities.basic_utilities import halve_into_two_ints
from textwrap import fill

# ---------------
def remove_list_formatting(user_list: str):
    user_list = str(user_list)[1:-1]
    return user_list.replace("'", "")

# ---------------
def pad_string(
        string: str,
        target_len: int,
        pad_char: str = " ",
        prefix: bool = True,
        affix: bool = True,
        ) -> str:
    """utility function to pad strings to make them a desired length. Used primarily for keeping
    ASCII art correct while still allowing string formatting.
    note that 'prefix' and 'affix' denote whether the padding should come before or after the string
    (or before AND after if both parameters are True).
    """
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


# ---------------
def dict_to_formatted_string(
        obj: dict | list,
        prefix: str = " | ",
        indent: int = 0,
        keys_to_ignore: list[str] = [],
        len_limit=70,
        ) -> str:
    """
    Function to custom format a dictionary as a string that can then be printed as an indented list
    """
    string = ""
    indent_add = 3
    indent_str = " "

    if isinstance(obj, dict):
        for key, val in obj.items():
            if key in keys_to_ignore:
                continue
            curr_prefix = f"{prefix}{indent * indent_str}"
            # where value is not another nested object, just add "key: value" with no extra indents.
            if not isinstance(val, dict) and not isinstance(val, list):
                # If string will be longer than given len_limit, then split onto multiple lines
                string += fill(
                    text=f"{key}: {val}",
                    width=len_limit,
                    initial_indent=curr_prefix,
                    subsequent_indent=curr_prefix + (indent_str * indent_add),
                )
                string += "\n"
            else:
                string += f"{curr_prefix}{key}:\n"
                string += dict_to_formatted_string(
                    val, prefix,
                    indent + indent_add,
                    keys_to_ignore
                )
    elif isinstance(obj, list):
        for elem in obj:
            string += dict_to_formatted_string(elem, prefix, indent, keys_to_ignore)
    else:
        curr_prefix = f"{prefix}{indent * indent_str}"
        # If string will be longer than given len_limit, then split onto multiple lines
        string += fill(
            text=obj,
            width=len_limit,
            initial_indent=curr_prefix,
            subsequent_indent=curr_prefix + (indent_str * indent_add),
        )
        string += "\n"
    return string