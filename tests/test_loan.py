#!/usr/bin/env python3

import unittest
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
sys.path.append('../src')
import config as cfg
import loan
import exceptions
import tools
from debt import Debt


class TestLoan(unittest.TestCase):
    def setUp(self):
        # Resetting class variables between tests
        loan.Loan.counter = 1
        loan.Loan.actives = []
        loan.Loan.closed = []
        loan.Loan.df_input_loans = None
        # Show all rows/columns when pandas DF is printed
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', None)
        pd.set_option('display.max_colwidth', None)



    def test_invalid_loan_csv_data(self):
        cfg.set_test_mode('loans_0.csv')
        self.assertRaises(exceptions.InvalidData, loan.init_loans)

    def test_single_loan_no_collateral_updates(self):
        cfg.set_test_mode('loans_1.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.actives), 1, 'Should be 1 loan')
        self.assertEqual(len(loan.Loan.actives[0].collateral_history), 1,
                         "Should be 1 entry in collateral history")
        self.assertEqual(loan.Loan.actives[0].current_collateral, 1.0,
                         'Should be 1.0 in total collateral')
        df_stats = loan.Loan.actives[0].stats
        self.assertEqual(df_stats[df_stats['date'] == '2020-01-31']['fx_cadusd'].values[0],
                         "0.7557", 'Should be 0.7557 in fx rate')
        self.assertEqual(df_stats[df_stats['date'] == '2020-01-24']['fx_cadusd'].values[0],
                         "0.7610", 'Should be 0.7610 in fx rate')

    def test_single_loan_multiple_collateral_increases(self):
        cfg.set_test_mode('loans_2.csv')
        loan.init_loans()
        df_stats = loan.Loan.actives[0].stats
        self.assertEqual(len(loan.Loan.actives[0].collateral_history), 3,
                         "Should be 3")
        self.assertEqual(loan.Loan.actives[0].current_collateral, 6.0,
                         'Should be 6.0 in current collateral')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-01']['coll_amount'].values[0],
                         1.0, 'Should be 1.0 in coll_amount')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-10']['coll_amount'].values[0],
                         3.0, 'Should be 3.0 in coll_amount')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-20']['coll_amount'].values[0],
                         6.0, 'Should be 6.0 in coll_amount')

    def test_multiple_loans_multiple_collateral_increases(self):
        cfg.set_test_mode('loans_3.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.actives), 2, "Should be 2")
        self.assertEqual(loan.Loan.actives[0].current_collateral, 3.0,
                         'Should be 3.0 in current collateral')
        self.assertEqual(loan.Loan.actives[1].current_collateral, 10.0,
                         'Should be 10.0 in current collateral')
        self.assertEqual(len(loan.Loan.actives[0].collateral_history), 2, "Should be 2")
        self.assertEqual(len(loan.Loan.actives[1].collateral_history), 4, "Should be 4")
        df_stats0 = loan.Loan.actives[0].stats
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-10-01']['coll_amount'].values[0],
                         1.0, 'Should be 1.0 in coll_amount')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-10-15']['coll_amount'].values[0],
                         3.0, 'Should be 3.0 in coll_amount')
        df_stats1 = loan.Loan.actives[1].stats
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-01']['coll_amount'].values[0],
                         1.0, 'Should be 1.0 in coll_amount')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-12']['coll_amount'].values[0],
                         3.0, 'Should be 3.0 in coll_amount')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-13']['coll_amount'].values[0],
                         6.0, 'Should be 6.0 in coll_amount')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-15']['coll_amount'].values[0],
                         10.0, 'Should be 10.0 in coll_amount')

    def test_single_loan_multiple_collateral_decreases(self):
        cfg.set_test_mode('loans_4.csv')
        loan.init_loans()
        df_stats = loan.Loan.actives[0].stats
        self.assertEqual(len(loan.Loan.actives[0].collateral_history), 3,
                         "Should be 3")
        self.assertEqual(loan.Loan.actives[0].current_collateral, 5.0,
                         'Should be 5.0 in current collateral')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-01']['coll_amount'].values[0],
                         10.0, 'Should be 10.0 in coll_amount')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-10']['coll_amount'].values[0],
                         8.0, 'Should be 3.0 in coll_amount')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-20']['coll_amount'].values[0],
                         5.0, 'Should be 5.0 in coll_amount')

    def test_single_loan_multiple_collateral_increases_and_decreases(self):
        cfg.set_test_mode('loans_5.csv')
        loan.init_loans()
        df_stats = loan.Loan.actives[0].stats
        self.assertEqual(len(loan.Loan.actives[0].collateral_history), 5,
                         "Should be 5")
        self.assertEqual(loan.Loan.actives[0].current_collateral, 4.0,
                         'Should be 4.0 in current collateral')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-01']['coll_amount'].values[0],
                         8.0, 'Should be 8.0 in coll_amount')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-10']['coll_amount'].values[0],
                         10.0, 'Should be 10.0 in coll_amount')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-20']['coll_amount'].values[0],
                         9.0, 'Should be 9.0 in coll_amount')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-21']['coll_amount'].values[0],
                         7.0, 'Should be 7.0 in coll_amount')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-22']['coll_amount'].values[0],
                         4.0, 'Should be 4.0 in coll_amount')

    def test_multiple_loans_multiple_cad_borrowed_increases(self):
        cfg.set_test_mode('loans_6.csv')
        loan.init_loans()
        self.assertEqual(loan.Loan.actives[0].current_debt_cad, 10000,
                         'Should be 10000 in current cad debt')
        self.assertEqual(loan.Loan.actives[1].current_debt_cad, 6000,
                         'Should be 6000 in current cad debt')
        self.assertEqual(len(loan.Loan.actives[0].debt_history_cad), 4, "Should be 4 updates")
        self.assertEqual(len(loan.Loan.actives[1].debt_history_cad), 3, "Should be 3 updates")
        df_stats0 = loan.Loan.actives[0].stats
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-01']['debt_cad'].values[0],
                         1000, 'Should be 1000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-04']['debt_cad'].values[0],
                         1000, 'Should be 1000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-05']['debt_cad'].values[0],
                         3000, 'Should be 3000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-09']['debt_cad'].values[0],
                         3000, 'Should be 3000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-10']['debt_cad'].values[0],
                         6000, 'Should be 6000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-19']['debt_cad'].values[0],
                         6000, 'Should be 6000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-20']['debt_cad'].values[0],
                         10000, 'Should be 10000 in debt_cad')
        df_stats1 = loan.Loan.actives[1].stats
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-01']['debt_cad'].values[0],
                         1000, 'Should be 1000 in debt_cad')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-10']['debt_cad'].values[0],
                         3000, 'Should be 3000 in debt_cad')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-20']['debt_cad'].values[0],
                         6000, 'Should be 60000 in debt_cad')

    def test_multiple_loans_multiple_updates_in_collateral_and_cad_borrowed(self):
        cfg.set_test_mode('loans_7.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.actives), 2, "Should be 2 active_loans loans")
        self.assertEqual(loan.Loan.actives[0].current_collateral, 4.0,
                         'Should be 4.0 in current collateral')
        self.assertEqual(loan.Loan.actives[1].current_collateral, 10.0,
                         'Should be 10.0 in current collateral')
        self.assertEqual(loan.Loan.actives[0].current_debt_cad, 3000,
                         'Should be 3000 in current cad debt')
        self.assertEqual(loan.Loan.actives[1].current_debt_cad, 6000,
                         'Should be 6000 in current cad debt')

        self.assertEqual(len(loan.Loan.actives[0].collateral_history), 4, "Should be 4 updates")
        self.assertEqual(len(loan.Loan.actives[1].collateral_history), 3, "Should be 3 updates")
        df_stats0 = loan.Loan.actives[0].stats
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-01']['coll_amount'].values[0],
                         10.0, 'Should be 10.0 in coll_amount')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-04']['coll_amount'].values[0],
                         10.0, 'Should be 10.0 in coll_amount')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-05']['coll_amount'].values[0],
                         7.0, 'Should be 7.0 in coll_amount')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-06']['coll_amount'].values[0],
                         7.0, 'Should be 7.0 in coll_amount')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-10']['coll_amount'].values[0],
                         8.0, 'Should be 8.0 in coll_amount')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-11']['coll_amount'].values[0],
                         8.0, 'Should be 8.0 in coll_amount')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-21']['coll_amount'].values[0],
                         4.0, 'Should be 4.0 in coll_amount')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-22']['coll_amount'].values[0],
                         4.0, 'Should be 4.0 in coll_amount')

        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-01']['debt_cad'].values[0],
                         1000, 'Should be 1000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-21']['debt_cad'].values[0],
                         1000, 'Should be 1000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-22']['debt_cad'].values[0],
                         3000, 'Should be 1000 in debt_cad')
        self.assertEqual(df_stats0[df_stats0['date'] == '2019-11-23']['debt_cad'].values[0],
                         3000, 'Should be 1000 in debt_cad')

        df_stats1 = loan.Loan.actives[1].stats
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-01']['coll_amount'].values[0],
                         10.0, 'Should be 1.0 in coll_amount')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-09']['coll_amount'].values[0],
                         10.0, 'Should be 1.0 in coll_amount')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-10']['coll_amount'].values[0],
                         5.0, 'Should be 5.0 in coll_amount')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-11']['coll_amount'].values[0],
                         5.0, 'Should be 5.0 in coll_amount')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-20']['coll_amount'].values[0],
                         10.0, 'Should be 6.0 in coll_amount')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-21']['coll_amount'].values[0],
                         10.0, 'Should be 10.0 in coll_amount')

        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-01']['debt_cad'].values[0],
                         1000, 'Should be 1000 in debt_cad')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-19']['debt_cad'].values[0],
                         1000, 'Should be 1000 in debt_cad')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-20']['debt_cad'].values[0],
                         6000, 'Should be 60000 in debt_cad')
        self.assertEqual(df_stats1[df_stats1['date'] == '2019-11-21']['debt_cad'].values[0],
                         6000, 'Should be 60000 in debt_cad')

    def test_collateralization_ratio(self):
        cfg.set_test_mode('loans_8.csv')
        loan.init_loans()
        df_stats0 = loan.Loan.actives[0].stats
        self.assertEqual(round(df_stats0[df_stats0['date'] == '2019-11-01']['ltv'].values[0], 2),
                         0.49, 'Should be 0.49 in LTV')
        self.assertEqual(round(df_stats0[df_stats0['date'] == '2019-11-02']['ltv'].values[0], 2),
                         0.33, 'Should be 0.33 in LTV')
        self.assertEqual(round(df_stats0[df_stats0['date'] == '2019-11-03']['ltv'].values[0], 2),
                         0.40, 'Should be 0.40 in LTV')
        self.assertEqual(round(df_stats0[df_stats0['date'] == '2019-11-04']['ltv'].values[0], 2),
                         0.42, 'Should be 0.42 in LTV')

    def test_updating_ratio_with_current_price(self):
        cfg.set_test_mode('loans_9.csv')
        loan.init_loans()
        df_stats0 = loan.Loan.actives[0].stats
        self.assertEqual(round(df_stats0[df_stats0['date'] == '2019-11-01']['ltv'].values[0], 2),
                         0.49, 'Should be 0.49 in LTV')
        new_price_usd = 15000.0
        loan.update_loans_with_current_price(price_given=new_price_usd)
        date_to_update = tools.get_current_date_for_exchange_api()
        df_stats0 = loan.Loan.actives[0].stats

        self.assertEqual(df_stats0[df_stats0['date'] == date_to_update]['btc_price_usd'].values[0],
                         new_price_usd, 'Should be '+str(new_price_usd)+' in btc_price_usd')
        coll_amount = df_stats0.loc[df_stats0['date'] == date_to_update, 'coll_amount'].values[0]
        debt_cad = df_stats0.loc[df_stats0['date'] == date_to_update, 'debt_cad'].values[0]
        interest_cad = df_stats0.loc[df_stats0['date'] == date_to_update, 'interest_cad'].values[0]
        new_price_cad = df_stats0.loc[df_stats0['date'] == date_to_update, 'btc_price_cad'].values[0]
        new_ratio = round((debt_cad + interest_cad) / (coll_amount * new_price_cad), 2)
        self.assertEqual(round(df_stats0[df_stats0['date'] == date_to_update]['ltv'].values[0], 2),
                         new_ratio, 'Should be new ltv')

    def test_adding_new_row_to_stats(self):
        cfg.set_test_mode('loans_10.csv')
        loan.init_loans()
        date_not_in_stats = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        price = 123456.0
        loan.update_loans_with_current_price(date_given=date_not_in_stats, price_given=price)
        df_stats0 = loan.Loan.actives[0].stats
        self.assertEqual(df_stats0[df_stats0['date'] == date_not_in_stats]['btc_price_usd'].values[0],
                         price, 'Should be the price in the new stats entry')
        loan0 = loan.Loan.actives[0]
        prev_interest_accrued = df_stats0.iloc[1]['interest_cad']
        curr_interest_accrued = round(prev_interest_accrued + (cfg.LOAN_DAILY_INTEREST * loan0.current_debt_cad), 1)
        self.assertEqual(round(df_stats0[df_stats0['date'] == date_not_in_stats]['interest_cad'].values[0], 1),
                         curr_interest_accrued, 'Interest in new row appended incorrect')

    def test_accrued_interest(self):
        cfg.set_test_mode('loans_11.csv')
        loan.init_loans()
        df_stats0 = loan.Loan.actives[0].stats
        stats_interest = df_stats0[df_stats0['date'] == pd.to_datetime('2019-12-01')]['interest_cad'].values[0]
        self.assertEqual(3.29, stats_interest, "Should be 3.29 interest")
        stats_interest = df_stats0[df_stats0['date'] == pd.to_datetime('2019-12-04')]['interest_cad'].values[0]
        self.assertEqual(13.16, stats_interest, "Should be 13.16 interest")
        stats_interest = df_stats0[df_stats0['date'] == pd.to_datetime('2019-12-05')]['interest_cad'].values[0]
        self.assertEqual(19.74, stats_interest, "Should be 19.74 interest")
        stats_interest = df_stats0[df_stats0['date'] == pd.to_datetime('2019-12-06')]['interest_cad'].values[0]
        self.assertEqual(27.96, stats_interest, "Should be 27.96 interest")
        stats_interest = df_stats0[df_stats0['date'] == pd.to_datetime('2019-12-07')]['interest_cad'].values[0]
        self.assertEqual(36.19, stats_interest, "Should be 36.19 interest")
        stats_interest = df_stats0[df_stats0['date'] == pd.to_datetime('2019-12-08')]['interest_cad'].values[0]
        self.assertEqual(44.41, stats_interest, "Should be 44.41 interest")

    def test_loan_prod_1(self):
        cfg.set_test_mode('loans_12.csv')
        loan.init_loans()
        df_debt = Debt().build_dataframe()
        self.assertEqual(round(df_debt[df_debt['date'] == '2019-12-15']['total_liab_cad'].values[0], 1),
                         10844.8, 'Total liabilities CAD do not match')

    def test_loan_prod_2(self):
        cfg.set_test_mode('loans_13.csv')
        loan.init_loans()
        df_debt = Debt().build_dataframe()
        self.assertEqual(round(df_debt[df_debt['date'] == '2019-12-15']['total_liab_cad'].values[0], 1),
                         43116.2, 'Total liabilities CAD do not match')

    def test_cost_loan_analysis(self):
        cfg.set_test_mode('loans_14.csv')
        loan.init_loans()
        res = loan.get_cost_analysis()
        i = 0
        for cdp in loan.Loan.actives:
            start_total_debt = round((cdp.stats.iloc[-1]['debt_cad'] +
                                      cdp.stats.iloc[-1]['interest_cad'] +
                                      cdp.admin_fee), 4)
            start_cost_btc = round(start_total_debt / cdp.stats.iloc[-1]['btc_price_cad'], 4)
            end_total_debt = round((cdp.stats.iloc[0]['debt_cad'] +
                                    cdp.stats.iloc[0]['interest_cad'] +
                                    cdp.admin_fee), 4)
            end_cost_btc = round(end_total_debt / cdp.stats.iloc[0]['btc_price_cad'], 4)
            diff = round(end_cost_btc - start_cost_btc, 4)
            self.assertEqual(res["diff_btc"][i], diff, "Should be " + str(diff))
            i += 1
        self.assertEqual(res["diff_btc"][-1], round(res["diff_btc"][0] + res["diff_btc"][1], 4),
                         "Incorrect Total difference btc amount")

    def test_closed_loan(self):
        cfg.set_test_mode('loans_15.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.actives), 1, 'Should be 1 active loan')
        self.assertEqual((loan.Loan.actives[0]).id, 2, 'Should be active loan ID:2 ')
        self.assertEqual(len(loan.Loan.closed), 2, 'Should be 2 closed loans')
        self.assertEqual((loan.Loan.closed[0]).id, 1, 'Should be closed loan ID:1 ')
        self.assertEqual((loan.Loan.closed[1]).id, 3, 'Should be closed loan ID:3 ')

if __name__ == '__main__':
    unittest.main()

