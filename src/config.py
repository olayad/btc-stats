TEST_MODE = 0
LOANS_INPUT_FILE = '../data/loans.csv'
SAVINGS_INPUT_FILE = '../data/savings.csv'
INTEREST_INPUT_FILE = '../data/interest.csv'

# TODO: change below to loan_daily_interest
DAILY_INTEREST = 0.000329

# Loan movement types
NEW_LOAN = 0
COLLATERAL_INCREASED = 1
COLLATERAL_DECREASED = 2
DEBT_CAD_INCREASED = 3
CLOSED_LOAN = 4

# Savings movement types
INCREASE = 0
DECREASE = 1

def set_test_mode(test_case):
    global TEST_MODE
    TEST_MODE = test_case


def set_loans_input_file(input_file):
    global LOANS_INPUT_FILE
    LOANS_INPUT_FILE = input_file


