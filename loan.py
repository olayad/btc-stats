import pandas as pd

class Loan:
    counter = 0
    active_loans = None

    def __init__(self, loan_amount, date_coll_recv, wallet_address, coll_amount):
        global counter
        self.loan_amount = loan_amount
        self.date_coll_recv = date_coll_recv
        self.wallet_address = wallet_address
        self.coll_amount = coll_amount
        self.id = Loan.counter
        Loan.counter += 1

    def to_string(self):
        return 'id:{:2d}, amount:${:5d}, collateral_amount:{:8.4} '.format(self.counter,
                                                                           self.loan_amount,
                                                                           self. coll_amount)

def load_loans():
    df = None
    Loan.active_loans = []

    try:
        df = pd.read_csv('./data/loans.csv')
    except FileNotFoundError:
        print('ERROR - File loans.csv not found, terminating program')
        exit(1)
    df.set_index('num', inplace=True)

    for index, row in df.iterrows():
        cdp = Loan(df['loan_amount'],
                   df['date_coll_recv'],
                   df['wallet_address'],
                   df['coll_amount'])
        Loan.active_loans.append(cdp)
        print('Appended: ', cdp)

def get_loans():
    if Loan.active_loans is None:
        print('get_loans - about to load_loans for first time')
        load_loans()
    else:
        return Loan.active_loans
