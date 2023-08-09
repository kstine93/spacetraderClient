"""
Basic functional programming utilities portable across applications
"""

# ==========
import json
import pwinput
from math import floor, ceil
from datetime import datetime,timedelta
from typing import Iterator
from os import listdir, remove, fsdecode, getenv, environ, path


# ==========
def get_user_password(prompt: str, password_name: str, double_entry: bool=False) -> str:
    """Get user password from environment variables - or prompt and store if it
    doesn't exist yet. Double-entry requires user to provide password twice to check consistency."""
    pw = getenv(password_name)
    if pw is None:
        pw2 = None
        while True:
            pw = pwinput.pwinput(prompt=prompt,mask="*")
            if double_entry:
                pw2 = pwinput.pwinput(prompt="Please enter your password again: ",mask="*")
                if pw != pw2:
                    print("Passwords did not match - please try again.\n")
                    continue
            break
        environ[password_name] = pw
    return pw




# =======================
# = DATA TRANSFORMATION =
# =======================
def dict_vals_to_list(obj: dict) -> list:
    return list(obj.values())


# ==========
def bytes_to_dict(bytes_obj: bytes, format: str = "utf-8") -> dict:
    return json.loads(bytes_obj.decode(format))


# ==========
def dict_to_bytes(dict_obj: dict, format: str = "utf-8") -> bytes:
    return dict_obj.encode(format)


# ==========
def empty_directory(dir_path: str):
    """Remove all files from a directory"""
    for file in listdir(dir_path):
        file_path = f"{dir_path}/{fsdecode(file)}"
        remove(file_path)

# ==========
def dedup_list(list:list) -> list:
    return [*set(list)]


def halve_into_two_ints(dividend:int,first_high:bool=False) -> tuple[int]:
    '''Divides integers by '2' and returns a tuple with the results. If the dividend is even, the
    returned numbers are identical. If the dividend is odd, the function still ensures two integers
    are returned by assigning either the first or second item the 'higher' value. For example,
    dividend = 7 would yield (4,3) or (3,4) depending on the value of 'first_high'.
    Dividend = 10 would always yield (5,5).
    '''
    if first_high:
        return (ceil(dividend/2), floor(dividend/2))
    else:
        return (floor(dividend/2), ceil(dividend/2))


# ==========
def time_diff_seconds(utc_time_str: str, format: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> int:
    """Find difference between given UTC time and current local time in seconds"""
    time_diff = get_time_diff_UTC(utc_time_str,format)
    return int(time_diff.total_seconds())

# ==========
def get_time_diff_UTC(utc_time_str: str, format: str = "%Y-%m-%dT%H:%M:%S.%fZ") -> int:
    """Find difference between given UTC time and current local time in seconds"""
    utc_time = datetime.strptime(utc_time_str, format)
    diff = utc_time - datetime.utcnow()
    no_microseconds_diff = diff - timedelta(microseconds = diff.microseconds)
    return no_microseconds_diff


# ==============
# = JSON FILES =
# ==============
def get_files_in_dir(dir_path) -> Iterator[str]:
    """For a directory with a list of JSON files, get all first-level keys from the files"""
    for file in listdir(dir_path):
        yield f"{dir_path}/{fsdecode(file)}"


# ==========
def get_keys_in_dir(dir_path) -> Iterator[str]:
    """For a directory with a list of JSON files, get all first-level keys from the files"""
    for file in get_files_in_dir(dir_path):
        for key in get_keys_in_file(file):
            yield key


# ==========
def count_keys_in_dir(dir_path) -> int:
    """Counts keys across all (JSON) files in a directory"""
    return sum(1 for key in get_keys_in_dir(dir_path))


# ==========
def count_keys_in_file(file_path: str) -> int:
    """Counts keys in JSON file"""
    return sum(1 for key in get_keys_in_file(file_path))


# ==========
def get_keys_in_file(file_path: str) -> Iterator[str]:
    """Returns all first-level keys in JSON file"""
    with open(file_path, "r") as file:
        for key in json.loads(file.read()).keys():
            yield key


# ==========
def get_dict_from_file(file_path: str) -> dict:
    """Reads and returns dict from file"""
    with open(file_path, "r") as file:
        return json.loads(file.read())


# ==========
def write_dict_to_file(file_path: str, data: dict) -> None:
    """Writes provided dict to file"""
    with open(file_path, "w") as file:
        file.write(json.dumps(data, indent=3))


# ==========
def attempt_dict_retrieval(file_path: str) -> dict:
    """Attempts to get data as dictionary from file"""
    if path.exists(file_path) and path.getsize(file_path) > 0:
        return get_dict_from_file(file_path)
    else:
        return {}


# ==========
def remove_dict_record_if_exists(file_path: str, key: str):
    """Delete dict object if it exists"""
    data = attempt_dict_retrieval(file_path)
    if key in data.keys():
        del data[key]
        write_dict_to_file(file_path, data)
