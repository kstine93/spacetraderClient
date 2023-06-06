"""
Code for testing the 'contracts' class
"""

#==========
from src.utilities.basic_utilities import empty_directory
from os import path
from collections import Counter
from src.contracts import *
import unittest

#==========
class TestContracts(unittest.TestCase):
    """Unit testing for 'contracts' class"""
    #----------
    contract_name = "clija6w677t03s60d7ctvf8ec"
    contracts_filepath = "./gameData/contracts/"
    contract_schema = ['id','factionSymbol','type','terms','accepted','fulfilled','expiration','deadlineToAccept']
    contract = Contracts()

    #----------
    def test_get_without_cache(self):
        empty_directory(self.contracts_filepath)
        data = self.contract.get_contract(self.contract_name)
        record = data[self.contract_name]
        self.assertEqual(Counter(record.keys()), Counter(self.contract_schema))

    def test_reload_cache(self):
        empty_directory(self.contracts_filepath)
        data = self.contract.list_all_contracts()
        record = data[self.contract_name]
        self.assertEqual(Counter(record.keys()), Counter(self.contract_schema))


if __name__ == '__main__':
    unittest.main()