#!/usr/bin/env python3

import unittest
import sys
import argparse

import test_loan
import test_debt
import test_tools


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test to run.')
    parser.add_argument('testcase', metavar='N', nargs='+',
                        help='an integer for the accumulator')
    args = parser.parse_args()
    print("args", args.testcase)

    loader = unittest.TestLoader
    suite = unittest.TestSuite()

    for test in args.testcase:
        if test == "loans" or test == "loan" or test == "loan.py":
            suite.addTest(unittest.makeSuite(test_loan.TestLoan))
        if test == "tools" or test == "tool" or test == "tools.py":
            suite.addTest(unittest.makeSuite(test_tools.TestTools))
        if test == "debt":
            suite.addTest(unittest.makeSuite(test_debt.TestDebt))

    result = unittest.TextTestRunner(verbosity=1).run(suite)
    sys.exit(not result.wasSuccessful())
