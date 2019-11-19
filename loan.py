import pandas as pd

class Loan:
    counter = 1
    active_loans = None
    df_loans = None
    df_btcusd = None

    def __init__(self, loan_amount, date_coll_recv, wallet_address, coll_amount):
        global counter
        self.loan_amount = loan_amount
        self.date_coll_recv = date_coll_recv
        self.wallet_address = wallet_address
        self.coll_amount = coll_amount
        self.id = Loan.counter
        Loan.counter += 1

    def generate_loan_stats(self):
        if Loan.df_btcusd is None:
            load_price_data()
        calculate_loan_ratios()




        

    def calculate_loan_ratios(self):


    def __str__(self):
        return 'Loan_id:{:0>2d}, ' \
               'amount:${:6d}, ' \
               'collateral_amount:{} '.format(self.id, self.loan_amount, self.coll_amount)

def load_price_data():
    global df_btcusd
    try:
        df_btcusd = pd.read_csv('./data/loans.csv')
    except FileNotFoundError:
        print('[Error] File btcusd.csv not found, terminating program')
        exit(1)
    df_btcusd['Date'] = pd.to_datetime(df_btcusd['Date'])
    df_btcusd['Last'] = pd.to_numeric(df_btcusd['Last'])

def load_loans():
    global df_loans
    Loan.active_loans = []
    try:
        df_loans = pd.read_csv('./data/loans.csv')
    except FileNotFoundError:
        print('[ERROR] File loans.csv not found, terminating program')
        exit(1)
    df_loans.set_index('num', inplace=True)

    for index, row in df_loans.iterrows():
        cdp = Loan(row['loan_amount'],
                   row['date_coll_recv'],
                   row['wallet_address'],
                   row['coll_amount'])
        Loan.active_loans.append(cdp)

        # REMOVE HOOK
        if cdp.id == 7:
            generate_loan_stats()



def get_loans():
    if Loan.active_loans is None:
        print('[INFO] get_loans - Loading loan.csv info for first time')
        load_loans()
    return Loan.active_loans
