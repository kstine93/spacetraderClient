from typing import Callable
import json

'''
UPDATING LOCAL CACHE
'''
def check_single_record_then_call_and_update(self,file_path:str,func:Callable,new_key:str,**kwargs) -> dict:
    try:
        #Try to open local cache and return record. If this fails, pull from API:
        with open (file_path, "r") as file:
            existing_data = json.loads(file.read())
        return existing_data['new_key']
    except:
        data = func(new_key)
        return call_and_update(data,file_path)


def call_and_update(self,data:dict,file_path:str) -> dict:
    try:
        #Try to get file (but not sure it exists):
        with open (file_path, "r") as file:
            existing_data = json.loads(file.read())
    except:
        #If getting file failed, we replace file:
        existing_data = {}
    finally:
        existing_data.update(data)
        with open (file_path, "r") as file:
            file.write(json.dumps(data,indent=3))
    return data



'''
DEALING WITH API DATA
'''

@check_single_record_then_call_and_update
def get_API_record_single(new_key:str) -> dict:
    #This can be FORCE UPDATE or GET LOCAL
    data = "getAPIRecord(self,url,body)"
    return data

# COULD THIS BE A GENERIC DECORATOR? This could take a function which returns a page of data.
# THIS COULD BE IN CACHE MANAGER CLASS WITH THE NAME 'cache_nested_records' or something like that.
def get_API_record_page() -> dict:
    #For multiple records, there is no "check if I have it first". I am calling the API because I am not relying
    #on a local cache - therefore DECORATOR FUNCTIONALITY IS UNNECESSARY.
    #This will always be: FORCE UPDATE
    data = "getAPIRecord(self,url,body)"
    for record in data:
        call_and_update(record,path="file_path")

# IF THE FUNCTION ABOVE GETS MADE INTO A DECORATOR, THIS ONE COULD TOO - COULD TAKE A GENERATOR FUNCTION THAT PRODUCES
# NESTED JSON OBJECTS, WHICH THEN THEMSELVES GET ITERATED OVER.
# NOTE: This might assume a lot about how the objects are nested though - might be safer to do on an individual basis.
def get_API_record_paginated() -> dict:
    #For multiple records, there is no "check if I have it first". I am calling the API because I am not relying
    #on a local cache - therefore DECORATOR FUNCTIONALITY IS UNNECESSARY.
    #This will always be: FORCE UPDATE
    for data in "getAPIRecord(self,url,body)":
        for record in data:
            call_and_update(record,path="file_path")