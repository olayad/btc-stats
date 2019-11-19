#!/usr/bin/env python3

import unittest
import sys

print(sys.path)
print(sys.builtin_module_names)
class TestLoanClass (unittest.TestCase):

    def test_create_loan(self):
        print('waka')
