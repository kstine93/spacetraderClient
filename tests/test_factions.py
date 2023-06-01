"""
Code for testing the 'factions' class
"""

#==========
from src.utilities.basic_utilities import empty_directory
from os import path
from collections import Counter
from src.factions import *
import unittest

#==========
class TestFactions(unittest.TestCase):
    """Unit testing for 'factions' class"""
    #----------
    faction_schema = ["symbol","name","description","headquarters","traits","isRecruiting"]
    faction_filepath = "./gameData/factions/"
    faction = Factions()

    #----------
    def test_get_without_cache(self):
        empty_directory(self.faction_filepath)
        data = self.faction.get_faction("VOID")
        self.assertEqual(Counter(data.keys()), Counter(self.faction_schema))

    def test_reload_cache(self):
        empty_directory(self.faction_filepath)
        data = self.faction.list_all_factions()
        record = data["COSMIC"]
        self.assertEqual(Counter(record.keys()), Counter(self.faction_schema))


if __name__ == '__main__':
    unittest.main()

