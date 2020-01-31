#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.realpath('.'))
import unittest
import tools
import datetime

class TestTools(unittest.TestCase):
    # Kraken information contains next day info after 1600 PST, hence this tests
    # should account for that extra entry.

    def test_get_rates_all_week_days(self):
        resp = tools.get_fx_cadusd_rates(start_date='2019-11-04', end_date='2019-11-08')
        print(resp)
        # if datetime.datetime.now().hour >= 16:
        #     self.assertEqual(len(resp), 6, 'Should be 6')
        # else:
        self.assertEqual(len(resp), 5, 'Should be 5')
    #
    # def test_get_rates_holiday_first_day(self):
    #     # Nov 11th is holiday
    #     resp = tools.get_fx_cadusd_rates(start_date='2019-11-11', end_date='2019-11-14')
    #     if datetime.datetime.now().hour >= 16:
    #         self.assertEqual(len(resp), 5, 'Should be 5')
    #     else:
    #         self.assertEqual(len(resp), 4, 'Should be 4')
    #
    # def test_get_rates_only_holiday(self):
    #     # Nov 11th is holiday
    #     resp = tools.get_fx_cadusd_rates(start_date='2019-11-11', end_date='2019-11-11')
    #     if datetime.datetime.now().hour >= 16:
    #         self.assertEqual(len(resp), 2, 'Should be 2')
    #     else:
    #         self.assertEqual(len(resp), 1, 'Should be 1')
    #     self.assertEqual(resp[0], tools.AVG_FXCADUSD, 'Should be equal to AVG_FXCADUSD')
    #
    # def test_get_rates_weekend_between(self):
    #     resp = tools.get_fx_cadusd_rates(start_date='2019-10-28', end_date='2019-11-04')
    #     if datetime.datetime.now().hour >= 16:
    #         self.assertEqual(len(resp), 9, 'Should be 9')
    #     else:
    #         self.assertEqual(len(resp), 8, 'Should be 8')
    #
    # def test_get_rates_weekend_start(self):
    #     resp = tools.get_fx_cadusd_rates(start_date='2019-11-02', end_date='2019-11-09')
    #     if datetime.datetime.now().hour >= 16:
    #         self.assertEqual(len(resp), 9, 'Should be 9')
    #     else:
    #         self.assertEqual(len(resp), 8, 'Should be 8')
    #
    # def test_get_rates_weekend_end(self):
    #     resp = tools.get_fx_cadusd_rates(start_date='2019-11-08', end_date='2019-11-10')
    #     if datetime.datetime.now().hour >= 16:
    #         self.assertEqual(len(resp), 4, 'Should be 4')
    #     else:
    #         self.assertEqual(len(resp), 3, 'Should be 3')
    #
    # def test_get_rates_only_weekend(self):
    #     resp = tools.get_fx_cadusd_rates(start_date='2019-11-09', end_date='2019-11-10')
    #     if datetime.datetime.now().hour >= 16:
    #         self.assertEqual(len(resp), 3, 'Should be 3')
    #     else:
    #         self.assertEqual(len(resp), 2, 'Should be 2')


if __name__ == '__main__':
    unittest.main()
