#!/usr/bin/env python3

import unittest
import sys
import os
sys.path.append(os.path.realpath('../src'))
import config as cfg
import loan
from debt import Debt


class TestDebt(unittest.TestCase):

    def test_debt_dataframe(self):
        cfg.set_test_mode('debt_1.csv')
        loan.init_loans()
        df_debt = Debt().build_dataframe()
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-01']['debt_cad'].values[0],
                         20020, 'Debt cad should be 20020')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-02']['debt_cad'].values[0],
                         20020, 'Debt cad should be 20020')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-03']['debt_cad'].values[0],
                         30030, 'Debt cad should be 30030')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-05']['debt_cad'].values[0],
                         40040, 'Debt cad should be 40040')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-06']['debt_cad'].values[0],
                         40040, 'Debt cad should be 40040')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-06']['debt_cad'].values[0],
                         40040, 'Debt cad should be 40040')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-01']['interest_cad'].values[0],
                         6.58, 'Interest should be 6.58')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-02']['interest_cad'].values[0],
                         13.16, 'Interest should be 13.16')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-03']['interest_cad'].values[0],
                         23.03, 'Interest should be 23.03')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-04']['interest_cad'].values[0],
                         32.90, 'Interest should be 32.90')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-05']['interest_cad'].values[0],
                         46.06, 'Interest should be 46.06')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-06']['interest_cad'].values[0],
                         59.22, 'Interest should be 59.22')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-07']['interest_cad'].values[0],
                         88.83, 'Interest should be 88.83')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-01']['interest_btc'].values[0],
                         0.0007, 'Interest should be .0007')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-07']['interest_btc'].values[0],
                         0.0089, 'Interest should be .0089')
        self.assertEqual(round(df_debt[df_debt['date'] == '2019-12-07']['debt_btc'].values[0], 1),
                         9.0, 'Interest should be 9.0')
        df_stats0 = loan.Loan.actives[0].stats
        btc_price_stats = df_stats0[df_stats0['date'] == '2019-12-01']['btc_price_cad'].values[0]
        btc_price_debt = df_debt[df_debt['date'] == '2019-12-01']['btc_price_cad'].values[0]
        self.assertEqual(btc_price_debt, btc_price_stats, 'BTC price is not equal in both dataframes')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-01']['total_liab_cad'].values[0],
                         20026.58, 'Total liabilities CAD do not match')
        self.assertEqual(df_debt[df_debt['date'] == '2019-12-07']['total_liab_cad'].values[0],
                         90148.83, 'Total liabilities CAD do not match')
        self.assertEqual(round(df_debt[df_debt['date'] == '2019-12-07']['total_liab_btc'].values[0], 1),
                         9.1, 'Total liabilities BTC do not match')

    def test_closed_loan(self):
        cfg.set_test_mode('debt_2.csv')
        loan.init_loans()
        df_debt = Debt().build_dataframe()
        self.assertEqual(round(df_debt[df_debt['date'] == '2020-03-15']['debt_cad'].values[0], 1),
                         2020, 'Debt cad should be 2020')
        self.assertEqual(round(df_debt[df_debt['date'] == '2020-03-16']['debt_cad'].values[0], 1),
                         2020, 'Debt cad should be 2020')
        self.assertEqual(round(df_debt[df_debt['date'] == '2020-03-17']['debt_cad'].values[0], 1),
                         1010, 'Debt cad should be 1010')

        self.assertEqual(round(df_debt[df_debt['date'] == '2020-03-15']['total_liab_cad'].values[0], 2),
                         2020.66, 'Total liab cad should be 2020.66')
        self.assertEqual(round(df_debt[df_debt['date'] == '2020-03-16']['total_liab_cad'].values[0], 2),
                         2021.32, 'Total liab cad should be 2021.32')
        self.assertEqual(round(df_debt[df_debt['date'] == '2020-03-17']['total_liab_cad'].values[0], 2),
                         1010.99, 'Total liab cad should be 1010.99')
        self.assertEqual(round(df_debt[df_debt['date'] == '2020-03-18']['total_liab_cad'].values[0], 2),
                         1011.32, 'Total liab cad should be 1011.32')



if __name__ == '__main__':
    unittest.main()
