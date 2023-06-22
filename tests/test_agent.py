"""
Code for testing the 'agents' class
"""

#==========
from src.utilities.basic_utilities import empty_directory
from os import path
from collections import Counter
from src.base import *
import unittest

#==========
class TestAgents(unittest.TestCase):
    """Unit testing for 'agents' class"""
    #----------
    agent_schema = ['accountId','symbol','headquarters','credits','startingFaction']
    stc = SpaceTraderConnection()

    #----------
    def test_get_agent(self):
        data = self.stc.get_agent()
        self.assertEqual(Counter(data.keys()), Counter(self.agent_schema))

if __name__ == '__main__':
    unittest.main()