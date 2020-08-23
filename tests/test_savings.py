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
        # Resetting class variables between tests
        savings.Savings.balance_btc = 0
        # Show all rows/columns when pandas DF is printed
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', -1)

    def test_invalid_csv_file(self):
            cfg.set_test_mode('savings_does_not_exist.csv')
            self.assertRaises(exceptions.InitializationDataNotFound, savings.init_savings, 'rates_0.csv')

    def test_invalid_savings_data(self):
        cfg.set_test_mode('savings_0.csv')
        self.assertRaises(exceptions.InvalidData, savings.init_savings, 'rates_0.csv')

    def test_sort_input_df(self):
        cfg.set_test_mode('savings_1.csv')
        savings.init_savings('rates_1.csv')
        self.assertEqual(savings.Savings.rates_input_df.iloc[0]['date'], '2020-06-01', 'Incorrect sort order')
        self.assertEqual(savings.Savings.account_input_df.iloc[0]['date'], '2020-08-01', 'Incorrect sort order')

        print(f'\n***Stats df***')
        print(savings.Savings.stats)

        print(f'\n***Rates df***')
        print(savings.Savings.rates_input_df)
        print(f'\n***Savings df**')
        print(savings.Savings.account_input_df)

    # def test_total_savings_btc(self):
    #     cfg.set_test_mode('savings_1.csv')
    #     savings.init_savings('rates_0.csv')
    #     self.assertEqual(savings.Savings.total_btc, 1.5, 'Should be 1.5')

    # def test_interest_rate_no_change(self):
    #     cfg.set_test_mode('savings_2.csv')
    #     savings.init_savings('rates_0.csv')
    #     savings_df = savings.Savings.account_input_df
    #     rates_df = savings.Savings.rates_input_df
    #
    #     print('\n***Savings_df***')
    #     print(savings_df)
    #
    #     print('\n***rates_df***')
    #     print(rates_df)


if __name__ == '__main__':
    unittest.main()

