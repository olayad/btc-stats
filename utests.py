#!/usr/bin/env python3

import unittest
import sys
import tools

class TestLoanClass (unittest.TestCase):

    def test_get_rates_continous_week_days(self):
        resp = tools.get_cadusd_rates(start_date='2019-11-04', end_date='2019-11-08')
        self.assertEqual(len(resp), 5, 'Should be 5')

    # def test_get_rates_holiday(self):
    #     # Nov 11th is holiday
    #     resp = tools.get_cadusd_rates(start_date='2019-11-11', end_date='2019-11-15')
    #     self.assertEqual(len(resp), 5, 'Should be 5')

if __name__ == '__main__':
    unittest.main()