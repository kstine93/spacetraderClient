"""
Code for testing the 'agents' class
"""

#==========
from src.utilities.basic_utilities import empty_directory
from os import path
from collections import Counter
from src.agent import *
import unittest

#==========
class TestAgents(unittest.TestCase):
    """Unit testing for 'agents' class"""
    #----------
    agent_callsign = "AMBROSIUS-RITZ"
    agent_filepath = f"./gameData/agents/"
    agent_schema = ['accountId','symbol','headquarters','credits','startingFaction']
    agent = Agent()

    #----------
    def test_get_without_cache(self):
        empty_directory(self.agent_filepath)
        data = self.agent.get_agent(self.agent_callsign)
        self.assertEqual(Counter(data.keys()), Counter(self.agent_schema))

if __name__ == '__main__':
    unittest.main()