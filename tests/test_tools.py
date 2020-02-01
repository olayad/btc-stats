#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.realpath('.'))
import unittest
import tools


class TestTools(unittest.TestCase):

    def test_fx_rates(self):
        resp = tools.get_fx_cadusd_rates(start_date='2020-01-26', end_date='2020-01-31')
        self.assertEqual(len(resp), 6, 'Should be 6')
        self.assertEqual(float(resp[5]), 0.753, "Should be rate of 0.753")
        self.assertEqual(float(resp[4]), 0.7586, "Should be rate of 0.7586")
        self.assertEqual(float(resp[3]), 0.7588, "Should be rate of 0.7588")
        self.assertEqual(float(resp[2]), 0.7578, "Should be rate of 0.7578")
        self.assertEqual(float(resp[1]), 0.7566, "Should be rate of 0.7566")
        self.assertEqual(float(resp[0]), 0.7557, "Should be rate of 0.7557")

    def test_get_rates_all_week_days(self):
        resp = tools.get_fx_cadusd_rates(start_date='2019-11-04', end_date='2019-11-08')
        self.assertEqual(len(resp), 5, 'Should be 5')
        self.assertEqual(float(resp[4]), 0.7606, "Should be rate of 0.7606")
        self.assertEqual(float(resp[3]), 0.7603, "Should be rate of 0.7603")
        self.assertEqual(float(resp[2]), 0.7588, "Should be rate of 0.7588")
        self.assertEqual(float(resp[1]), 0.7590, "Should be rate of 0.7590")
        self.assertEqual(float(resp[0]), 0.7563, "Should be rate of 0.7563")

    def test_get_rates_holiday_first_day(self):
        # Nov 11th is holiday
        resp = tools.get_fx_cadusd_rates(start_date='2019-11-11', end_date='2019-11-14')
        self.assertEqual(len(resp), 4, 'Should be 4')

    def test_get_rates_only_holiday(self):
        # Nov 11th is holiday
        resp = tools.get_fx_cadusd_rates(start_date='2019-11-11', end_date='2019-11-11')
        self.assertEqual(len(resp), 1, 'Should be 1')
        self.assertEqual(resp[0], tools.AVG_FXCADUSD, 'Should be equal to AVG_FXCADUSD')

    def test_get_rates_weekend_between(self):
        resp = tools.get_fx_cadusd_rates(start_date='2019-10-28', end_date='2019-11-04')
        self.assertEqual(len(resp), 8, 'Should be 8')

    def test_get_rates_weekend_start(self):
        resp = tools.get_fx_cadusd_rates(start_date='2019-11-02', end_date='2019-11-09')
        self.assertEqual(len(resp), 8, 'Should be 8')

    def test_get_rates_weekend_end(self):
        resp = tools.get_fx_cadusd_rates(start_date='2019-11-08', end_date='2019-11-10')
        self.assertEqual(len(resp), 3, 'Should be 3')

    def test_get_rates_only_weekend(self):
        resp = tools.get_fx_cadusd_rates(start_date='2019-11-09', end_date='2019-11-10')
        self.assertEqual(len(resp), 2, 'Should be 2')


if __name__ == '__main__':
    unittest.main()
