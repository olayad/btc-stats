#!/usr/bin/env/ python3
import pandas as pd
import datetime
import tools
from exceptions import InitializationDataNotFound
import sys
import os

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
        print(self.df_btcusd.head())
        print(self.df_loans.head())

        print('### Calculating loan_stats ###')
        print('### Rows greater than start date ###', self.start_date)
        date = pd.Timestamp(self.start_date)
        self.stats['date'] = self.df_btcusd[self.df_btcusd['Date'] >= date]['Date']
        self.stats['price'] = self.df_btcusd[self.df_btcusd['Date'] >= date]['Last']
        # self.stats['rates'] = tools.get_cadusd_rates(str(self.start_date))
        result = tools.get_cadusd_rates(str(self.start_date))
        print('shape:', self.stats.shape)
        print('result:', len(result))


        # TODO: There is a discrepancy on the number of rows that get_cadusd_rates
        # return and the number of rows that self.stats have


        print()
        print('stats df:')
        print(self.stats)


        sys.exit(1)

        # self.calculate_ratios()

    def calculate_ratios(self):
        return NotImplemented
    #     ratios = []
    #     for ind, row in self.stats.iterrows():
    #         ratios.append((row['Last'] * self.coll_amount) / self.loan_amount)
    #         print(ratios)
    #
    #         # TODO: Need to get the CAD FX on specific date
    #
    #
    #     self.stats['coll_ratio'] = ratios
    #     print('self.ratios:\n', self.stats)
    #     # TODO add calculated ratios to self.stats


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
        print('[INFO] Initializing loan info [loan.csv].')
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
    prod_path = './data/loans.csv'
    test_path = './tests/loans'+str(test_mode)+'.csv'
    try:
        df_loans = pd.read_csv(test_path) if test_mode else pd.read_csv(prod_path)
    except FileNotFoundError:
        print('[ERROR] Could not find file [/data/loan.csv].')
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
    df_btcusd['Last'] = pd.to_numeric(df_btcusd['Last'])
    return df_btcusd


def create_loan_instances():
    active_loans = []
    for index, row in Loan.df_loans.iterrows():
        cdp = Loan(row['loan_amount'],
                   row['date_coll_recv'],
                   row['wallet_address'],
                   row['coll_amount'])
        active_loans.append(cdp)
    return active_loans
