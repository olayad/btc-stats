#!/usr/bin/env/ python3
import pandas as pd
import datetime
import tools
from exceptions import InitializationDataNotFound


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
        rates = tools.get_cadusd_rates(str(self.start_date))


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


def get_loans():
    if Loan.active_loans is None:
        print('[INFO] Initializing loan info [loan.csv].')
        init_loans()
    return Loan.active_loans


def init_loans():
    Loan.active_loans = []
    load_loans_data()
    tools.update_btcusd_data()
    load_price_data()
    create_loan_instances()


def load_loans_data():
    try:
        Loan.df_loans = pd.read_csv('./data/loans.csv')
    except FileNotFoundError:
        print('[ERROR] Could not find file [/data/loan.csv].')
        raise InitializationDataNotFound
    Loan.df_loans.set_index('num', inplace=True)


def load_price_data():
    try:
        Loan.df_btcusd = pd.read_csv('./data/btcusd.csv')
    except FileNotFoundError:
        print('[ERROR] Could not find file [/data/btcusd.csv].')
        raise InitializationDataNotFound
    Loan.df_btcusd['Date'] = pd.to_datetime(Loan.df_btcusd['Date'])
    Loan.df_btcusd['Last'] = pd.to_numeric(Loan.df_btcusd['Last'])

def create_loan_instances():
    for index, row in Loan.df_loans.iterrows():
        cdp = Loan(row['loan_amount'],
                   row['date_coll_recv'],
                   row['wallet_address'],
                   row['coll_amount'])
        Loan.active_loans.append(cdp)
        # Todo: uncomment below, should calculate stats for all cdps
        # cdp.calculate_loan_stats()
        # Todo: remove following hook
        if cdp.id == 7:
            print(cdp)



            cdp.calculate_loan_stats()
