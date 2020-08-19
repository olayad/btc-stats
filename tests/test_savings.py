#!/usr/bin/env python3

import unittest
import sys
import os
sys.path.append('../src')
# from datetime import datetime, timedelta
import pandas as pd
import config as cfg
import savings
# import loan
import exceptions
# import tools
# from debt import Debt


class TestSavings(unittest.TestCase):
    def setUp(self):
        pass
        # Show all rows/columns when pandas DF is printed
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', -1)
    #
    # def test_invalid_csv_file(self):
    #     cfg.set_test_mode('savings_does_not_exist.csv')
    #     self.assertRaises(exceptions.InitializationDataNotFound, savings.init_savings)
    #
    # def test_incorrect_file(self):
    #     cfg.set_test_mode('savings_0.csv')
    #     self.assertRaises(exceptions.InvalidData, savings.init_savings)
    #
    # def test_total_savings_btc(self):
    #     cfg.set_test_mode('savings_1.csv')
    #     savings.init_savings()
    #     df = savings.Savings.input_file_df
    #     self.assertEqual(savings.Savings.total_btc, 2.5, 'Should be 2.5')
    #
    def test_interest_rate_change(self):
        cfg.set_test_mode('savings_2.csv')
        savings.init_savings()
        df = savings.Savings.input_file_df
        print(df)
        print(savings.Savings.interest_history_cad)
        print(f'interest_history len:{len(savings.Savings.interest_history_cad)}')

if __name__ == '__main__':
    unittest.main()

