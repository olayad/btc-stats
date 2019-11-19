import pandas as pd
import datetime

class Loan:
    counter = 1
    active_loans = None
    df_loans = None
    df_btcusd = None

    def __init__(self, loan_amount, date_coll_recv, wallet_address, coll_amount):
        global counter
        self.stats = pd.DataFrame()
        self.loan_amount = loan_amount
        self.start_date = datetime.datetime.strptime(date_coll_recv, '%Y/%m/%d')
        self.wallet_address = wallet_address
        self.coll_amount = coll_amount
        self.id = Loan.counter
        Loan.counter += 1

    def generate_stats(self):
        if Loan.df_btcusd is None:
            load_price_data()
        self.calculate_ratios()



    def calculate_ratios(self):
        global df_btcusd
        global df_loans
        print(df_btcusd.head())
        print(df_loans.head())

        print('\n\n### Rows greater than start date ###', self.start_date)
        self.stats['date'] = df_btcusd[df_btcusd['Date'] >= self.start_date]['Date']
        self.stats['price'] = df_btcusd[df_btcusd['Date'] >= self.start_date]['Last']

        ratios = []
        for ind, row in self.stats.iterrows():
            ratios.append((row['Last'] * self.coll_amount) / self.loan_amount)
            print(ratios)

            # TODO: Need to get the CAD FX on specific date


        self.stats['coll_ratio'] = ratios
        print('self.ratios:\n', self.stats)


    def __str__(self):
        return 'Loan_id:{:0>2d}, amount:${:6d}, ' \
               'collateral_amount:{}, start_date:{} '.format(self.id,
                                                             self.loan_amount,
                                                             self.coll_amount,
                                                             self.start_date)


def load_price_data():
    global df_btcusd
    try:
        df_btcusd = pd.read_csv('./data/btcusd.csv')
    except FileNotFoundError:
        print('[Error] File [/data/btcusd.csv] not found, terminating program')
        exit(1)
    df_btcusd['Date'] = pd.to_datetime(df_btcusd['Date'])
    df_btcusd['Last'] = pd.to_numeric(df_btcusd['Last'])


def load_loans():
    global df_loans
    Loan.active_loans = []
    try:
        df_loans = pd.read_csv('./data/loans.csv')
    except FileNotFoundError:
        print('[ERROR] File [/data/loans.csv] not found, terminating program')
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
            cdp.generate_stats()



def get_loans():
    if Loan.active_loans is None:
        print('[INFO] get_loans - Loading loan.csv info for first time')
        load_loans()

    # TODO: Update ratios here

    return Loan.active_loans
