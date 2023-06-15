"""
Code for testing the 'systems' class
"""

#==========
from src.utilities.basic_utilities import empty_directory,remove_dict_record_if_exists
from collections import Counter
from os import remove
from src.markets import *
import unittest

#==========
class TestMarkets(unittest.TestCase):
    """Unit testing for 'systems' class"""
    #----------

    market_waypoint = "X1-AG66-83180E"
    market_schema = ['symbol','imports','exports','exchange','tradeGoods']

    margin_schema = ['item','sell','buy','margin']

    market = Markets()

    #----------
    def test_get_market(self):
        data = self.market.get_market(self.market_waypoint)
        keys_counter = data[self.market_waypoint].keys()
        self.assertTrue(set(keys_counter).issubset(set(self.market_schema)))
        # self.assertEqual(keys_counter, Counter(self.market_schema))

    #----------
    def test_find_margin(self):
        data = self.market.find_margin("COPPER_ORE")
        keys_counter = Counter(data.keys())
        self.assertEqual(keys_counter, Counter(self.margin_schema))

    #----------
    def test_find_best_margins(self):
        limit = 3
        data = self.market.find_best_margins(limit)
        self.assertEqual(len(data),limit)
        keys_counter = Counter(data[0].keys())
        self.assertEqual(keys_counter, Counter(self.margin_schema))

    #----------
    def test_reload_cache(self):
        remove(self.market.price_chart_path)
        self.market.reload_price_chart_from_cache()
        self.test_find_margin()


if __name__ == '__main__':
    unittest.main()