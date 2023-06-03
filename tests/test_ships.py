"""
Code for testing the 'ships' class
"""

#==========
from collections import Counter
from src.ships import *
import unittest

#==========
class TestShips(unittest.TestCase):
    """
    Unit testing for 'ships' class.
    NOTE: Testing this class is tricky because many of the endpoints are NOT indempotent.
    Most endpoints (e.g., sell cargo) are editing the game state and could fail not due to
    any coding error, but rather due to an incompatible game state (ERR: no cargo to sell).
    Since this game state is very volatile, there is no easy way to create a stable set of
    tests here that covers these game-changing endpoints.
    Until I can figure out a better way to test everything, this will have to be enough.
    """
    #----------
    ship = Ships()
    ship_name = "AMBROSIUS-RITZ-1"

    #----------
    def test_get_ship(self):
        schema = ['symbol', 'nav', 'crew', 'fuel', 'frame', 'reactor', 'engine'
                    , 'modules', 'mounts', 'registration', 'cargo']
        data = self.ship.get_ship(self.ship_name)
        keys_counter = Counter(data['http_data']['data'].keys())
        self.assertEqual(keys_counter, Counter(schema))

    #----------
    def test_get_nav(self):
        schema = ['systemSymbol', 'waypointSymbol', 'route', 'status', 'flightMode']
        data = self.ship.get_nav_details(self.ship_name)
        keys_counter = Counter(data['http_data']['data'].keys())
        self.assertEqual(keys_counter, Counter(schema))

    #----------
    def test_get_cargo(self):
        schema = ['capacity', 'units', 'inventory']
        data = self.ship.get_current_cargo(self.ship_name)
        keys_counter = Counter(data['http_data']['data'].keys())
        self.assertEqual(keys_counter, Counter(schema))



if __name__ == '__main__':
    unittest.main()

