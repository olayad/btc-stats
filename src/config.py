TEST_MODE = 0
LOANS_INPUT_FILE = '../data/loans.csv'
SAVINGS_INPUT_FILE = '../data/savings.csv'
INTEREST_INPUT_FILE = '../data/interest.csv'
BTCUSD_INPUT_FILE = '../data/btcusd.csv'

LOAN_DAILY_INTEREST = 0.000329
AVG_FX_CADUSD = 0.80  # Last updated June, 2020

# Loan movement types
NEW_LOAN = 0
COLLATERAL_INCREASED = 1
COLLATERAL_DECREASED = 2
DEBT_CAD_INCREASED = 3
CLOSED_LOAN = 4

# Savings movement types
INCREASE = 0
DECREASE = 1

# Savings constants
DECIMALS = 8

# APIs
quandl_url = 'https://www.quandl.com/api/v3/datasets/BCHARTS/KRAKENUSD.csv?api_key=yynH4Pnq-X7AhiFsFdEa'
bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'
boc_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?'


def set_test_mode(test_case):
    global TEST_MODE
    TEST_MODE = test_case


def set_loans_input_file(file):
    global LOANS_INPUT_FILE
    LOANS_INPUT_FILE = file


def set_btcusd_input_file(file):
    global BTCUSD_INPUT_FILE
    BTCUSD_INPUT_FILE = file
