#!/usr/bin/env python3

import unittest
import sys
import os
sys.path.append(os.path.realpath('.'))
import loan

class TestLoan(unittest.TestCase):

    def test_single_loan_no_coll_updates(self):
        loan.set_test_mode('loans_coll_updates_1.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans[0].coll_history), 1, "Should be 1")

    def test_single_loan_single_coll_updates(self):
        loan.set_test_mode('loans_coll_updates_2.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans[0].coll_history), 2, "Should be 2")

    def test_multiple_loans_multiple_coll_updates(self):
        loan.set_test_mode('loans_coll_updates_3.csv')
        loan.init_loans()
        self.assertEqual(len(loan.Loan.active_loans), 2, "Should be 2")
        self.assertEqual(len(loan.Loan.active_loans[0].coll_history), 2, "Should be 2")
        self.assertEqual(len(loan.Loan.active_loans[1].coll_history), 4, "Should be 4")


if __name__ == '__main__':
    unittest.main()
