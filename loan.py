#!/usr/bin/env/ python3
import pandas as pd
import datetime
import tools
from exceptions import InitializationDataNotFound

TEST_MODE = 0
NEW_LOAN = 0
COLLATERAL_UPDATE = 1
CAD_BORROWED_UPDATE = 2


class Loan:
    counter = 1
    active_loans = []
    df_loans = None
    df_btcusd = None

    def __init__(self, start_date, wallet_address):
        self.stats = pd.DataFrame()
        self.collateral_history = {}    # {'date':'new collateral amount'}
        self.borrowed_cad_history = {}  # {'date':'new borrowed CAD amount'}
        self.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        self.wallet_address = wallet_address
        self.id = self.counter
        Loan.counter += 1

    def calculate_loan_stats(self):
        date = pd.Timestamp(self.start_date)
        self.stats['date'] = Loan.df_btcusd[Loan.df_btcusd['Date'] >= date]['Date']
        self.stats['usd_price'] = Loan.df_btcusd[Loan.df_btcusd['Date'] >= date]['Last']
        self.stats['fx_cadusd'] = tools.get_fx_cadusd_rates(str(self.start_date))
        self.stats['cad_price'] = [row['usd_price'] / float(row['fx_cadusd']) for _, row in self.stats.iterrows()]
        self.stats['cad_borrowed'] = self.populate_borrowed_cad()
        self.stats['collateral_amount'] = self.populate_collateral_amounts()
        self.stats['collateralization_ratio'] = self.calculate_collateralization_ratio()


        print(self.stats)

    def populate_borrowed_cad(self):
        borrowed_cad_values = []
        dates_which_had_borrowed_cad_update = list(self.borrowed_cad_history.keys())
        for index, row in self.stats.iterrows():
            borrowed_cad_values.append(self.borrowed_cad_history[dates_which_had_borrowed_cad_update[-1]])
            if row['date'] in dates_which_had_borrowed_cad_update:
                dates_which_had_borrowed_cad_update.pop()
        return borrowed_cad_values

    def populate_collateral_amounts(self):
        collateral_values = []
        dates_which_had_collateral_update = list(self.collateral_history.keys())
        for index, row in self.stats.iterrows():
            collateral_values.append(self.collateral_history[dates_which_had_collateral_update[-1]])
            if row['date'] in dates_which_had_collateral_update:
                dates_which_had_collateral_update.pop()
        return collateral_values

    def calculate_collateralization_ratio(self):
        pass
        # TODO: Ready to calculate this.
        # result = []
        # for index, row in self.stats.iterrows():
        #     result.append((row['cad_price'] * row['collateral_amount']) / row['cad_borrowed'])

    def __str__(self):
        return 'Loan_id:{:0>2d}, amount:${:6d}, ' \
               'collateral_history:{}, start_date:{} '.format(self.id,
                                                              self.borrowed_cad_history,
                                                              self.collateral_history,
                                                              self.start_date)


def set_test_mode(test_case):
    global TEST_MODE
    TEST_MODE = test_case


def get_loans():
    if len(Loan.active_loans) is 0:
        init_loans()
    return Loan.active_loans


def init_loans():
    load_dataframes()
    Loan.active_loans = create_loan_instances()
    for loan in Loan.active_loans: loan.calculate_loan_stats()


def load_dataframes():
    Loan.df_loans = load_loans_dataframe()
    tools.update_btcusd_csv()
    Loan.df_btcusd = load_price_dataframe()


def load_loans_dataframe():
    global TEST_MODE
    df_loans = None
    if TEST_MODE:
        try:
            test_path = './tests/data/'+str(TEST_MODE)
            print('[INFO] Initializing loans with file: '+test_path)
            df_loans = pd.read_csv(test_path)
        except FileNotFoundError:
            print('[ERROR] Could not find file [/tests/data' + str(TEST_MODE) + ']')
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
        if row['type'] is NEW_LOAN:
            active_loans.append(instantiate_new_loan(row))
            update_collateral_history(active_loans, row)
            update_borrowed_cad_history(active_loans, row)
        if row['type'] is COLLATERAL_UPDATE:
            update_collateral_history(active_loans, row)
        if row['type'] is CAD_BORROWED_UPDATE:
            update_borrowed_cad_history(active_loans, row)
    return active_loans


def instantiate_new_loan(entry):
    return Loan(entry['start_date'], entry['wallet_address'])


def update_collateral_history(loans, csv_entry):
    for cdp in loans:
        if cdp.wallet_address == csv_entry['wallet_address']:
            cdp.collateral_history.update({pd.Timestamp(csv_entry['date_update']): csv_entry['collateral_amount']})


def update_borrowed_cad_history(loans, csv_entry):
    for cdp in loans:
        if cdp.wallet_address == csv_entry['wallet_address']:
            cdp.borrowed_cad_history.update({pd.Timestamp(csv_entry['date_update']): csv_entry['cad_borrowed']})