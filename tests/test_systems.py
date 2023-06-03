"""
Code for testing the 'systems' class
"""

#==========
from src.utilities.basic_utilities import empty_directory,remove_dict_record_if_exists
from collections import Counter
from src.systems import *
import unittest

#==========
class TestSystems(unittest.TestCase):
    """Unit testing for 'systems' class"""
    #----------
    system_name = "X1-UF87"
    system_schema = ['symbol','sectorSymbol','type','x','y','waypoints','factions']
    system_filepath = "./gameData/systems/X1-A.json"

    market_waypoint = 'X1-HQ18-56588B'
    market_schema = ['symbol','imports','exports','exchange']

    shipyard_waypoint = 'X1-HQ18-60817D'
    shipyard_schema = ['symbol', 'shipTypes', 'transactions', 'ships']

    jump_gate_waypoint = 'X1-HQ18-58999A'
    jump_gate_schema = ['jumpRange', 'factionSymbol', 'connectedSystems']


    system = Systems()

    #----------
    def test_get_market(self):
        data = self.system.get_market(self.market_waypoint)
        keys_counter = Counter(data['http_data']['data'].keys())
        self.assertEqual(keys_counter, Counter(self.market_schema))

    #----------
    def test_get_shipyard(self):
        data = self.system.get_shipyard(self.shipyard_waypoint)
        keys_counter = Counter(data['http_data']['data'].keys())
        self.assertEqual(keys_counter, Counter(self.shipyard_schema))

    #----------
    def test_get_jump_gate(self):
        data = self.system.get_jump_gate(self.jump_gate_waypoint)
        keys_counter = Counter(data['http_data']['data'].keys())
        self.assertEqual(keys_counter, Counter(self.jump_gate_schema))

    #----------
    def test_get_system_without_cache(self):
        remove_dict_record_if_exists(self.system_filepath,self.system_name)
        data = self.system.get_system(self.system_name)
        keys_counter = Counter(data.keys())
        self.assertEqual(keys_counter,Counter(self.system_schema))

    #----------
    def test_reload_cache(self):
        #NOTE: This function takes a long time to run - and it is very similar to code in the
        #'contracts' and 'factions' code - so commenting it out for now (only test this
        # infrequently)
        pass
        # empty_directory(self.systems_filepath)
        # self.system.reload_systems_in_cache()
        # num_records = count_keys_in_dir(self.systems_filepath)
        # self.assertGreater(num_records,3000) #Should have at least 3k records.


if __name__ == '__main__':
    unittest.main()