"""
Basic functional programming utilities portable across applications
"""

#==========
import json
import getpass
from datetime import datetime
from time import tzname
from typing import Iterator
from os import listdir,remove,fsdecode,getenv,environ,path

#==========
def get_user_password(prompt:str,password_name:str) -> str:
    """Get user password from environment variables - or prompt and store if it
    doesn't exist yet."""
    pw = getenv(password_name)
    if pw is None:
        pw = getpass.getpass(prompt)
        environ[password_name] = pw
    return pw

#=======================
#= DATA TRANSFORMATION =
#=======================
def bytes_to_dict(bytes_obj:bytes,format:str = 'utf-8') -> dict:
    return json.loads(bytes_obj.decode(format))

#==========
def dict_to_bytes(dict_obj:dict, format:str = 'utf-8') -> bytes:
    return dict_obj.encode(format)

#==========
def empty_directory(dir_path:str):
    """Remove all files from a directory"""
    for file in listdir(dir_path):
        file_path = f"{dir_path}/{fsdecode(file)}"
        remove(file_path)

#==========
def time_seconds_diff_UTC(utc_time_str:str,format:str="%Y-%m-%dT%H:%M:%S.%fZ") -> int:
    """Find difference between given UTC time and current local time in seconds"""
    utc_time = datetime.strptime(utc_time_str,format)
    time_diff = utc_time - datetime.utcnow()
    return int(time_diff.total_seconds())


#==============
#= JSON FILES =
#==============
def get_keys_in_dir(dir_path) -> Iterator[str]:
    """For a directory with a list of JSON files, get all first-level keys from the files"""
    for file in listdir(dir_path):
        file_path = f"{dir_path}/{fsdecode(file)}"
        for key in get_keys_in_file(file_path):
            yield key

#==========
def count_keys_in_dir(dir_path) -> int:
    """Counts keys across all (JSON) files in a directory"""
    return sum(1 for key in get_keys_in_dir(dir_path))

#==========
def count_keys_in_file(file_path:str) -> int:
    """Counts keys in JSON file"""
    return sum(1 for key in get_keys_in_file(file_path))

#==========
def get_keys_in_file(file_path:str) -> Iterator[str]:
    """Returns all first-level keys in JSON file"""
    with open(file_path,"r") as file:
        for key in json.loads(file.read()).keys():
            yield key

#==========
def get_dict_from_file(file_path:str) -> dict:
    """Reads and returns dict from file"""
    with open (file_path, "r") as file:
        return json.loads(file.read())

#==========
def write_dict_to_file(file_path:str,data:dict) -> None:
    """Writes provided dict to file"""
    with open(file_path, "w") as file:
        file.write(json.dumps(data,indent=3))

#==========
def attempt_dict_retrieval(file_path:str) -> dict:
    """Attempts to get data as dictionary from file"""
    if path.exists(file_path) and path.getsize(file_path) > 0:
        return get_dict_from_file(file_path)
    else:
        return {}

#==========
def remove_dict_record_if_exists(file_path:str,key:str):
    """Delete dict object if it exists"""
    data = attempt_dict_retrieval(file_path)
    if key in data.keys():
        del data[key]
        write_dict_to_file(file_path,data)

