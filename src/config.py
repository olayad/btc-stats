TEST_MODE = 0
LOANS_INPUT_FILE = '../data/loans.csv'

NEW_LOAN = 0
COLLATERAL_INCREASED = 1
COLLATERAL_DECREASED = 2
DEBT_CAD_INCREASED = 3

DAILY_INTEREST = 0.000329


def set_test_mode(test_case):
    global TEST_MODE
    TEST_MODE = test_case


def set_loans_input_file(input_file):
    global LOANS_INPUT_FILE
    LOANS_INPUT_FILE = input_file
