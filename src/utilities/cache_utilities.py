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

# def print_sth(*args,**kwargs):
#     print(kwargs['file_path'])

# def test_cache(user_function):
#     def wrapper(*args, **kwargs):
#         #Do extra stuff
#         print(*args)
#         print(**kwargs)
#         result = user_function(*args, **kwargs)
#         return result
#     return wrapper





# class MyClass:
#     def __init__(self, file_path):
#         self.file_path = file_path

#     def key_cache(self):
#         return cache_wrapper(self.file_path)

#     @key_cache
#     def my_method(self, key):
#         # Method body



#def get_cache_dict_2(file_path,func,new_key):
# def get_cache_dict_2(file_path,func,new_key,*args,**kwargs):
#     existing_data = attempt_dict_retrieval(file_path)
#     if new_key in existing_data:
#         return existing_data[new_key]
#     else:
#         data = func(*args,**kwargs)
#         #data = func(new_key)
#         update_cache_dict(data,file_path)
#         return data[new_key]
    # cache_data = get_dict_from_file(cache_path)
    # if cache_data and new_key in cache_data:
    #     return cache_data[new_key]
    # else:
    #     result = func(new_key)
    #     if result:
    #         cache_data = cache_data or {}
    #         cache_data[new_key] = result
    #         with open(cache_path, 'w') as file:
    #             json.dump(cache_data, file)
    #     return result


# def get_cache_dict(self,file_path:str,new_key:str,func:Callable) -> dict:
#     """
#     This function is intended to be used as the core of a decorator function.
#     This function is for getting a single record that MIGHT be part of a bigger dict in
#     the local cache. The function first looks for the record in the dict (is given key present?)
#     If that fails becausethe cache file doesn't exist or the key is not present in the dict,
#     we call the given function (typically an API call) to find the data elsewhere.
#     We then pass the new data on to 'update_cache_dict' to update the cache.
#     """
#     existing_data = attempt_dict_retrieval(file_path)
#     if new_key in existing_data:
#         return existing_data[new_key]
#     else:
#         data = func(self,new_key)
#         #data = func(new_key)
#         update_cache_dict(data,file_path)
#         return data[new_key]


# import json
# from functools import wraps
# from src.utilities.basic_utilities import get_dict_from_file

# def check_faction_cache(cache_path):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(self, faction):
#             cache_data = get_dict_from_file(cache_path)
#             if cache_data and faction in cache_data:
#                 return cache_data[faction]
#             else:
#                 result = func(self, faction)
#                 if result:
#                     cache_data = cache_data or {}
#                     cache_data[faction] = result
#                     with open(cache_path, 'w') as file:
#                         json.dump(cache_data, file)
#                 return result
#         return wrapper
#     return decorator


# '''
# HOLY SHIT - this implementation with 'custom' seems to work!!!
# Let's test a little more to make sure, but if it does, this could be a much
# cleaner way to implement my caching, which doesn't require 'self' to be sent to the
# external caching function.

# Next Steps:
# 1. Test this more.
# 2. If it works, let's implement it as a standalone function (with correct caching logic)
#     and test with other classes.
# 3. If it looks stable, let's consider putting it in as another class method - since I DO still
#     like the idea of having a cache class... (not necessary though)
# 4. (LEARNING) - let's look more into what @wrap actually does - it seems like the only new thing
#     here, so it's probably critical for this working.
# '''
# def custom(cache_path,faction,func):
#     cache_data = get_dict_from_file(cache_path)
#     if cache_data and faction in cache_data:
#         return cache_data[faction]
#     else:
#         result = func(faction)
#         if result:
#             cache_data = cache_data or {}
#             cache_data[faction] = result
#             with open(cache_path, 'w') as file:
#                 json.dump(cache_data, file)
#         return result


# class Fact():
#     path = "./test.json"

#     def decorator(func):
#         #@wraps(func) #Seems redundant if I pass 'func' directly to the custom_function
#         def wrapper(self,faction):
#             path = self.path
#             return custom(path,faction,func)
#         return wrapper

#     #@check_faction_cache("./test.json")
#     @decorator
#     def get_faction(self, faction):
#         """Get information about a specific faction"""
#         url = self.base_url + "/" + faction
#         response = self.stc.stc_http_request(method="GET", url=url)
#         # Transforming returned data to be compatible with factions dict:
#         return {faction: response['http_data']['data']}