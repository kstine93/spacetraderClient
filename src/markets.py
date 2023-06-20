"""
Data and functions related for interacting with the 'systems' endpoint of the Spacetrader API
"""
#==========
from typing import Callable
from .base import SpaceTraderConnection
from .utilities.custom_types import SpaceTraderResp,PriceRecord,PriceObj,MarginObj
from .utilities.cache_utilities import dict_cache_wrapper,update_cache_dict
from .utilities.basic_utilities import (attempt_dict_retrieval,write_dict_to_file,get_files_in_dir
    ,get_keys_in_file,dict_vals_to_list)

#==========
class Markets:
    """
    Class to query and edit game data related to systems.
    """
    #----------
    stc = SpaceTraderConnection()
    base_url: str
    cache_path: str
    price_chart_path: str

    #For the price chart, how many values should we store per commodity (i.e., the best 5 prices).
    #More prices gives flexibility in finding a good market, but there are diminishing returns.
    price_chart_cutoff:int = 3

    #----------
    def __init__(self):
        self.base_url = self.stc.base_url + "/systems"
        self.cache_path = self.stc.base_cache_path + "markets/"
        self.price_chart_path = self.stc.base_cache_path + "price_chart.json"

    #----------
    def __mold_market_dict(self,response:SpaceTraderResp) -> dict:
        """Transform systems data into an easier-to-use format for inserting into dictionaries"""
        if not self.stc.response_ok(response): raise Exception(response)
        data = response['http_data']['data']
        data = self.__simplify_market_dict(data)
        return {data['symbol']:data}

    #----------
    def __simplify_market_dict(self,market_dict:dict[str,dict]) -> dict:
        """Transform market data into an easier-to-use format with less extra data"""
        market_dict.pop("transactions",None) #Removing info on past transactions
        for key in ['imports','exports','exchange']:
            market_dict[key] = [item['symbol'] for item in market_dict[key]]
        return market_dict

    #----------
    def __create_cache_path(self,system:str) -> str:
        """Create cache path from system string. To shard data, we're using the first 4
        characters of the system string as the file path (only last character varies A-Z)"""
        return self.cache_path + system[0:4] + ".json"

    #----------
    def cache_market(func: Callable) -> Callable:
        """
        Wrapper for an external, generic caching system.
        Passes a file path created from system variables and the 'waypoint' argument of the
        target function as values to the caching system to use in caching the data.
        Target function and its needed arguments (self,waypoint) also passed on.
        """
        def wrapper(self,waypoint:str):
            system = self.stc.get_system_from_waypoint(waypoint)
            path = self.__create_cache_path(system)
            return dict_cache_wrapper(file_path=path,key=waypoint)(func)(self,waypoint)
        return wrapper

    #----------
    @cache_market
    def get_market(self,waypoint:str) -> dict:
        """Returns information about what commodities may be bought/sold at a market waypoint"""
        system = self.stc.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/market"
        response = self.stc.stc_http_request(method="GET",url=url)
        data = self.__mold_market_dict(response)
        return data

    #----------
    def update_market(self,waypoint:str) -> dict:
        """gets market data and force-updates market cache. Called when we have new market data"""
        system = self.stc.get_system_from_waypoint(waypoint)
        url = f"{self.base_url}/{system}/waypoints/{waypoint}/market"
        response = self.stc.stc_http_request(method="GET",url=url)
        data = self.__mold_market_dict(response)
        file_path = self.__create_cache_path(system)
        update_cache_dict(data,file_path)
        self.update_price_chart(data[waypoint])
        return data[waypoint]

    #------------------------
    #--PRICE CHART CREATION--
    #------------------------
    def __create_price_obj(self) -> PriceObj:
        return {
            "purchase_prices": {},
            "sell_prices": {}
        }

    #----------
    def __update_price_obj(self,price_obj:PriceObj,new_record:PriceRecord,waypoint:str) -> PriceObj:
        new_purchase = {waypoint:new_record["purchasePrice"]}
        price_obj["purchase_prices"] = self.__add_to_price_records(
            price_obj['purchase_prices']
            ,new_purchase
            ,low_best=True)

        new_sell = {waypoint:new_record["sellPrice"]}
        price_obj["sell_prices"] = self.__add_to_price_records(
            price_obj["sell_prices"]
            ,new_sell
            ,low_best=False)

        return price_obj

    #----------
    def __add_to_price_records(self,prev_records:PriceRecord,new_record:PriceRecord,low_best:bool) -> PriceRecord:
        """Add price_record to price_obj so that price_obj has the best X values, where X is
        the value given by 'cutoff'. """
        prev_records.update(new_record)

        if len(prev_records.items()) > self.price_chart_cutoff:
            #Each run of this function should at most increment the number of items by 1.
            #If we exceed our cutoff, remove the record with the worst value.
            worst_price_record = self.__get_worst_price_record(prev_records,low_best)
            worst_price_key = list(worst_price_record.keys())[0]
            del prev_records[worst_price_key]
        return prev_records

    #----------
    def update_price_chart(self,market_dict:dict) -> None:
        """Updates cached price chart with provided market data"""
        path = self.price_chart_path
        price_chart = attempt_dict_retrieval(path)
        waypoint = market_dict['symbol']
        if 'tradeGoods' not in market_dict.keys(): #If market data doesn't have pricing information
            return None
        for item in market_dict['tradeGoods']:
            sym = item['symbol']
            #If the commodity is already listed in the chart:
            if sym not in price_chart.keys():
                price_chart[sym] = self.__create_price_obj()
            price_chart[sym] = self.__update_price_obj(price_chart[sym],item,waypoint)
        write_dict_to_file(path,price_chart)


    #----------
    def reload_price_chart_from_cache(self) -> None:
        """Recreate price chart from all market data from the cache."""
        for file_path in get_files_in_dir(self.cache_path):
            markets_obj = attempt_dict_retrieval(file_path)
            for key in markets_obj.keys():
                self.update_price_chart(markets_obj[key])


    #-----------------
    #--PRICE FINDING--
    #-----------------
    def find_margin(self,item:str) -> MarginObj:
        """Find optimal margins for buying + selling a particular commodity."""
        price_chart = attempt_dict_retrieval(self.price_chart_path)
        price_obj = price_chart[item]
        best_sell_obj = self.__get_best_price_record(price_obj['sell_prices'],low_best=False)
        best_buy_obj = self.__get_best_price_record(price_obj['purchase_prices'],low_best=True)
        margin = list(best_sell_obj.values())[0] - list(best_buy_obj.values())[0]
        return {
            "item":item,
            "sell":best_sell_obj,
            "buy":best_buy_obj,
            "margin":margin
        }

    #----------
    def find_best_margins(self,limit:int=3) -> list[MarginObj]:
        """Find the best margins across all commodity groups"""
        commodities = get_keys_in_file(self.price_chart_path)
        margins = [self.find_margin(item) for item in commodities]
        margins.sort(key=lambda obj: obj['margin'],reverse=True)
        return margins[0:limit]

    #----------
    def __get_best_price_record(self,price_records:PriceRecord,low_best:bool) -> PriceRecord:
        """For getting the record in a price object that is highest / lowest"""
        if low_best:
            best_price_key = min(price_records,key=price_records.get)
        else:
            best_price_key = max(price_records,key=price_records.get)
        return {best_price_key:price_records[best_price_key]}

    #----------
    def __get_worst_price_record(self,price_records:PriceRecord,low_best:bool) -> PriceRecord:
        low_best_reversed = not low_best
        return self.__get_best_price_record(price_records,low_best_reversed)