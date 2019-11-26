#!/usr/bin/env/ python3
import pandas as pd
import datetime
import tools
from exceptions import InitializationDataNotFound
import sys

test_mode = 0


class Loan:
    counter = 1
    active_loans = None
    df_loans = None
    df_btcusd = None

    def __init__(self, loan_amount, date_coll_recv, wallet_address, coll_amount):
        self.stats = pd.DataFrame()
        self.loan_amount = loan_amount
        self.start_date = datetime.datetime.strptime(date_coll_recv, '%Y/%m/%d').date()
        self.wallet_address = wallet_address
        self.coll_amount = coll_amount
        self.id = self.counter
        Loan.counter += 1

    def calculate_loan_stats(self):
        # print('\n### calculating loan_stats() ###')
        # print('start_date:', self.start_date)
        date = pd.Timestamp(self.start_date)

        self.stats['date'] = Loan.df_btcusd[Loan.df_btcusd['Date'] >= date]['Date']
        self.stats['usd_price'] = Loan.df_btcusd[Loan.df_btcusd['Date'] >= date]['Last']
        self.stats['fx_cadusd'] = tools.get_fx_cadusd_rates(str(self.start_date))
        self.stats['cad_price'] = [row['usd_price'] / float(row['fx_cadusd']) for _, row in self.stats.iterrows()]

    def __str__(self):
        return 'Loan_id:{:0>2d}, amount:${:6d}, ' \
               'collateral_amount:{}, start_date:{} '.format(self.id,
                                                             self.loan_amount,
                                                             self.coll_amount,
                                                             self.start_date)


def set_test_mode(suite):
    global test_mode
    test_mode = suite


def get_loans():
    if Loan.active_loans is None:
        init_loans()
    return Loan.active_loans


def init_loans():
    Loan.active_loans = []
    Loan.df_loans = load_loans_dataframe()
    tools.update_btcusd_csv()
    Loan.df_btcusd = load_price_dataframe()
    Loan.active_loans = create_loan_instances()

    for loan in Loan.active_loans:
        loan.calculate_loan_stats()



def load_loans_dataframe():
    global test_mode
    df_loans = None
    if test_mode:
        try:
            test_path = './tests/'+str(test_mode)
            print('[INFO] Initializing loans with file: '+test_path)
            df_loans = pd.read_csv(test_path)
        except FileNotFoundError:
            print('[ERROR] Could not find file [/tests/' +str(test_mode)+']')
            raise InitializationDataNotFound
    else:
        try:
            prod_path = './data/loans.csv'
            print('[INFO] Initializing loans with file: '+prod_path)
            df_loans = pd.read_csv(prod_path)
        except FileNotFoundError:
            print('[ERROR] Could not find file [/data/loans.csv].')
            raise InitializationDataNotFound
    df_loans.set_index('num', inplace=True)
    return df_loans


def load_price_dataframe():
    df_btcusd = None
    try:
        df_btcusd = pd.read_csv('./data/btcusd.csv')
    except FileNotFoundError:
        print('[ERROR] Could not find file [/data/btcusd.csv].')
        raise InitializationDataNotFound
    df_btcusd['Date'] = pd.to_datetime(df_btcusd['Date'])
    df_btcusd['Last'] = pd.to_numeric(df_btcusd['Close'])

    return df_btcusd

# def append_current_btc_price(df_btcusd):
#     today = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
#     price = tools.get_usd_price()
#     new_row = pd.DataFrame({'Date': [today], 'Open': ['NA'], 'High': ['NA'], 'Low': ['NA'],
#                             'Close': [price], 'Volume (BTC)': ['NA'],
#                             'Volume (Currency)': ['NA'], 'Weighted Price': ['NA']})
#     df_btcusd = pd.concat([new_row, df_btcusd], sort=True).reset_index(drop=True)
#     return df_btcusd

def create_loan_instances():
    active_loans = []
    for index, row in Loan.df_loans.iterrows():
        cdp = Loan(row['loan_amount'],
                   row['date_coll_recv'],
                   row['wallet_address'],
                   row['coll_amount'])
        active_loans.append(cdp)
    return active_loans
