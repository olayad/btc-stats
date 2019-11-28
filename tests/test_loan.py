#!/usr/bin/env python3

import unittest
import sys
import os
sys.path.append(os.path.realpath('.'))
import loan

class TestLoan(unittest.TestCase):

    def test_single_loan_no_coll_updates(self):
        loan.set_test_mode('loans_1.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans[0].collateral), 1, "Should be 1")

    def test_single_loan_single_coll_updates(self):
        loan.set_test_mode('loans_2.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans[0].collateral), 3, "Should be 3")

    def test_multiple_loans_multiple_coll_updates(self):
        loan.set_test_mode('loans_3.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans), 2, "Should be 2")
        self.assertEqual(len(loan.Loan.active_loans[0].collateral), 2, "Should be 2")
        self.assertEqual(len(loan.Loan.active_loans[1].collateral), 4, "Should be 4")

    def test_populate_collateral_values_single_amount(self):
        loan.set_test_mode('loans_1.csv')
        loan.init_loans()
        df_stats = loan.Loan.active_loans[0].stats
        self.assertEqual(len(loan.Loan.active_loans[0].stats['coll_amount'].unique()),
                         1, 'Should be 1 element')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-01']['coll_amount'].values[0],
                         1.0, 'Should be 1.0')

    def test_populate_collateral_values_multiple_updates(self):
        loan.set_test_mode('loans_2.csv')
        loan.init_loans()
        df_stats = loan.Loan.active_loans[0].stats
        self.assertEqual(len(df_stats['coll_amount'].unique()), 3, 'Should be 3 elements')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-20']['coll_amount'].values[0],
                         3.0, 'Should be 3.0')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-10']['coll_amount'].values[0],
                         2.0, 'Should be 2.0')
        self.assertEqual(df_stats[df_stats['date'] == '2019-11-01']['coll_amount'].values[0],
                         1.0, 'Should be 1.0')

    def test_populate_collateral_values_multiple_loans(self):
        loan.set_test_mode('loans_3.csv')
        loan.init_loans()
        df_stats = loan.Loan.active_loans[0].stats
        self.assertEqual(len(df_stats['coll_amount'].unique()), 2, 'Should be 2 elements')
        df_stats = loan.Loan.active_loans[1].stats
        self.assertEqual(len(df_stats['coll_amount'].unique()), 4, 'Should be 4 elements')


if __name__ == '__main__':
    unittest.main()

