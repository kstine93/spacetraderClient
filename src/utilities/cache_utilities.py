from .basic_utilities import *
from typing import Callable

#----------
def dict_cache_wrapper(file_path,key):
    """
    Generic caching function adapted for caching data as dictionaries in local files.
    Provided file path and key are used to locate and return records. If no matching record is
    found, the user_function is called and the data returned is used to update the cache.
    Note that updating the cache is kept as a separate function to allow force-updating the cache
    by calling this update function directly.
    """
    def decorator(user_function):
        def wrapper(*args, **kwargs):
            existing_data = attempt_dict_retrieval(file_path)
            if key in existing_data:
                #Wrapping result in new dict to be consistent with result of user_function:
                return {key:existing_data[key]}
            else:
                data = user_function(*args,**kwargs)
                update_cache_dict(data,file_path)
                return data[key]
        return wrapper
    return decorator

#----------
def update_cache_dict(data:dict,file_path:str) -> dict:
    """
    This function updates a local cache file with a given dictionary. If the file exists,
    we load the file data, update it with the given data, and re-write it. If the file
    doesn't exist, we make a new file with the provided data as the sole entry.
    Works specifically with dictionary data & .JSON files, but could be adapted for other formats.
    """
    existing_data = attempt_dict_retrieval(file_path)
    existing_data.update(data)
    write_dict_to_file(file_path,existing_data)