#!/usr/bin/env python3

import collections
import unittest
import sys
import os
sys.path.append('../src')
import pandas as pd
import config as cfg
import savings
import exceptions


class TestSavings(unittest.TestCase):
    def setUp(self):
        # Resetting class variables between tests
        savings.Savings.balance_btc = 0
        savings.Savings.daily_rate = 0
        savings.Savings.balance_history_btc = collections.OrderedDict()
        savings.Savings.daily_rate_history = collections.OrderedDict()

        # Show all rows/columns when pandas DF is printed
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', -1)
    #
    # def test_invalid_csv_file(self):
    #     cfg.set_test_mode('savings_does_not_exist.csv')
    #     self.assertRaises(exceptions.InitializationDataNotFound, savings.init_savings, 'rates_0.csv')
    #
    # def test_invalid_savings_data(self):
    #     cfg.set_test_mode('savings_0.csv')
    #     self.assertRaises(exceptions.InvalidData, savings.init_savings, 'rates_0.csv')
    #
    # def test_sort_input_df(self):
    #     cfg.set_test_mode('savings_1.csv')
    #     savings.init_savings('rates_0.csv')
    #     self.assertEqual(savings.Savings.rates_input_df.iloc[0]['date'], '2020-06-01', 'Incorrect sort order')
    #     self.assertEqual(savings.Savings.account_input_df.iloc[0]['date'], '2020-08-01', 'Incorrect sort order')
    #
    # def test_movements_btc(self):
    #     cfg.set_test_mode('savings_2.csv')
    #     savings.init_savings('rates_0.csv')
    #     self.assertEqual(savings.Savings.balance_btc, 10.5, 'Should be 10.5')
    #
    # def test_interest_rate_no_change(self):
    #     cfg.set_test_mode('savings_3.csv')
    #     savings.init_savings('rates_1.csv')
    #     stats = savings.Savings.stats
    #     # savings_df = savings.Savings.account_input_df
    #     # rates_df = savings.Savings.rates_input_df
    #     self.assertEqual(stats.iloc[0]['daily_rate'], 0.00328767, 'Wrong daily interest rate')
    #
    # def test_interest_rate_change(self):
    #     cfg.set_test_mode('savings_3.csv')
    #     savings.init_savings('rates_2.csv')
    #     stats = savings.Savings.stats
    #     # savings_df = savings.Savings.account_input_df
    #     # rates_df = savings.Savings.rates_input_df
    #     self.assertEqual(stats[stats['date'] == '2020-08-01']['daily_rate'].values[0], 0.00328767, 'Wrong daily rate')
    #     self.assertEqual(stats[stats['date'] == '2020-08-10']['daily_rate'].values[0], 0.00657534, 'Wrong daily rate')
    #
    # def test_movements_btc(self):
    #     cfg.set_test_mode('savings_4.csv')
    #     savings.init_savings('rates_2.csv')
    #     stats = savings.Savings.stats
    #     # savings_df = savings.Savings.account_input_df
    #     # rates_df = savings.Savings.rates_input_df
    #     self.assertEqual(stats[stats['date'] == '2020-08-01']['movements_btc'].values[0], 10, 'Wrong movement btc')
    #     self.assertEqual(stats[stats['date'] == '2020-08-05']['movements_btc'].values[0], 1, 'Wrong movement btc')
    #     self.assertEqual(stats[stats['date'] == '2020-08-15']['movements_btc'].values[0], -5, 'Wrong movement btc')
    #     self.assertEqual(stats[stats['date'] == '2020-08-20']['movements_btc'].values[0], 2.123456789, 'Wrong movement btc')
    #
    # def test_balance_btc(self):
    #     cfg.set_test_mode('savings_4.csv')
    #     savings.init_savings('rates_2.csv')
    #     stats = savings.Savings.stats
    #     # savings_df = savings.Savings.account_input_df
    #     # rates_df = savings.Savings.rates_input_df
    #     self.assertEqual(stats[stats['date'] == '2020-08-01']['balance_btc'].values[0], 10.000000, 'Wrong balance')
    #     self.assertEqual(stats[stats['date'] == '2020-08-02']['balance_btc'].values[0], 10.0328767, 'Wrong balance')
    #     self.assertEqual(stats[stats['date'] == '2020-08-05']['balance_btc'].values[0], 11.13215675, 'Wrong balance')
    #     self.assertEqual(stats[stats['date'] == '2020-08-06']['balance_btc'].values[0], 11.16875561, 'Wrong balance')
    #     self.assertEqual(stats[stats['date'] == '2020-08-11']['balance_btc'].values[0], 11.42809351, 'Wrong balance')
    #     self.assertEqual(stats[stats['date'] == '2020-08-15']['balance_btc'].values[0], 6.7316455, 'Wrong balance')
    #     self.assertEqual(stats[stats['date'] == '2020-08-20']['balance_btc'].values[0], 9.07934621, 'Wrong balance')
    #
    def test_get_monthly_balance(self):
        cfg.set_test_mode('savings_4.csv')
        savings.init_savings('rates_2.csv')
        stats = savings.Savings.stats
        # savings_df = savings.Savings.account_input_df
        # rates_df = savings.Savings.rates_input_df
        savings.get_monthly_interest_gains(month=8)
        # self.assertEqual(stats[stats['date'] == '2020-08-01']['balance_btc'].values[0], 10.000000, 'Wrong balance')


    # def test_production(self):
    #     cfg.set_test_mode('savings_5.csv')
    #     savings.init_savings('rates_3.csv')
    #     stats = savings.Savings.stats
    #     savings_df = savings.Savings.account_input_df
    #     rates_df = savings.Savings.rates_input_df
    #     print(savings.Savings.stats)
    #     print(f'\n***Rates df***')
    #     print(rates_df)
    #     print(f'\n***Savings df**')
    #     print(savings_df)


if __name__ == '__main__':
    unittest.main()

