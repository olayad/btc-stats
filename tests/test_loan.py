#!/usr/bin/env python3

import unittest
import sys
import os
sys.path.append(os.path.realpath('.'))
import loan

class TestLoan(unittest.TestCase):

    def test_single_loan_no_collateral_updates(self):
        loan.set_test_mode('loans_1.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans[0].collateral), 1, "Should be 1")

    def test_single_loan_two_collateral_updates(self):
        loan.set_test_mode('loans_2.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans[0].collateral), 3, "Should be 3")

    def test_multiple_loans_multiple_collateral_updates(self):
        loan.set_test_mode('loans_3.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans), 2, "Should be 2")
        self.assertEqual(len(loan.Loan.active_loans[0].collateral), 2, "Should be 2")
        self.assertEqual(len(loan.Loan.active_loans[1].collateral), 4, "Should be 4")

    def test_populate_collateral_values_single_amount(self):
        loan.set_test_mode('loans_1.csv')
        loan.init_loans()
        df_stats = loan.Loan.active_loans[0].stats
        self.assertEqual(len(loan.Loan.active_loans[0].stats['collateral_amount'].unique()),
                         1, 'Should be 1')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-01']['collateral_amount'].values[0],
                         1.0, 'Should be 1.0 in collateral')

    def test_populate_collateral_values_multiple_updates(self):
        loan.set_test_mode('loans_2.csv')
        loan.init_loans()
        df_stats = loan.Loan.active_loans[0].stats
        self.assertEqual(len(df_stats['collateral_amount'].unique()), 3, 'Should be 3 elements')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-20']['collateral_amount'].values[0],
                         3.0, 'Should be 3.0 in collateral')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-10']['collateral_amount'].values[0],
                         2.0, 'Should be 2.0 in collateral')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-01']['collateral_amount'].values[0],
                         1.0, 'Should be 1.0 in collateral')

    def test_multiple_updates_in_borrowed_cad(self):
        loan.set_test_mode('loans_4.csv')
        loan.init_loans()
        df_stats = loan.Loan.active_loans[0].stats
        self.assertEqual(len(df_stats['cad_borrowed'].unique()), 4,
                         'Should be 4 updates in cad borrowed')

    def test_multiple_updates_in_borrowed_cad_multiple_updates_same_day(self):
        loan.set_test_mode('loans_5.csv')
        loan.init_loans()
        df_stats = loan.Loan.active_loans[0].stats
        self.assertEqual(len(df_stats['cad_borrowed'].unique()), 3,
                         'Should be 3 updates in cad borrowed')



if __name__ == '__main__':
    unittest.main()

