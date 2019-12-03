#!/usr/bin/env/ python3
import pandas as pd
import datetime
import tools
from exceptions import InitializationDataNotFound, InvalidLoanData

TEST_MODE = 0
LOANS_INPUT_FILE = 'loans.csv'

NEW_LOAN = 0
COLLATERAL_INCREASED = 1
COLLATERAL_DECREASED = 2
CAD_BORROWED_INCREASED = 3


class Loan:
    counter = 1
    active_loans = []
    df_loans = None
    df_btcusd = None

    def __init__(self, start_date, wallet_address):
        self.stats = pd.DataFrame()
        self.collateral_history = {}    # {date:{'type': _ , 'amount': _}
        self.borrowed_cad_history = {}  # {date: amount}
        self.current_collateral = 0
        self.current_borrowed_cad = 0
        self.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        self.wallet_address = wallet_address
        self.id = self.counter
        Loan.counter += 1

    def calculate_loan_stats(self):
        date = pd.Timestamp(self.start_date)
        self.stats['date'] = Loan.df_btcusd[Loan.df_btcusd['Date'] >= date]['Date']
        self.stats['usd_price'] = Loan.df_btcusd[Loan.df_btcusd['Date'] >= date]['Last']
        self.stats['fx_cadusd'] = tools.get_fx_cadusd_rates(str(self.start_date))
        self.stats['cad_price'] = [round(row['usd_price'] / float(row['fx_cadusd']), 2) for _, row in self.stats.iterrows()]
        self.stats['borrowed_cad'] = self.populate_borrowed_cad()
        self.stats['collateral_amount'] = self.populate_collateral_amounts()
        self.stats['collateralization_ratio'] = self.calculate_collateralization_ratio()

    def populate_borrowed_cad(self):
        borrowed_cad_values = []
        dates_which_had_borrowed_cad_update = list(self.borrowed_cad_history.keys())
        curr_borrowed = self.current_borrowed_cad
        for index, row in self.stats.iterrows():
            borrowed_cad_values.append(curr_borrowed)
            if row['date'] in dates_which_had_borrowed_cad_update:
                curr_borrowed -= self.borrowed_cad_history[row['date']]
                dates_which_had_borrowed_cad_update.pop()
        return borrowed_cad_values

    def populate_collateral_amounts(self):
        collateral_values = []
        dates_which_had_collateral_update = list(self.collateral_history.keys())
        curr_collateral = self.current_collateral
        for index, row in self.stats.iterrows():
            collateral_values.append(curr_collateral)
            if row['date'] in dates_which_had_collateral_update:
                if self.collateral_history[row['date']]['type'] is COLLATERAL_INCREASED:
                    curr_collateral -= self.collateral_history[row['date']]['amount']
                else:
                    curr_collateral += self.collateral_history[row['date']]['amount']
                dates_which_had_collateral_update.pop()
        return collateral_values

    def calculate_collateralization_ratio(self):
        ratio_values = []
        for index, row in self.stats.iterrows():
            ratio = round((row['cad_price'] * row['collateral_amount']) / row['borrowed_cad'], 2)
            ratio_values.append(ratio)
        return ratio_values

    def update_stats_entry(self, date_to_update, price, column='usd_price'):
        self.stats.loc[self.stats['date'] == date_to_update, column] = price
        self.recalculate_collateralization_ratio_by_date(date_to_update)

    def recalculate_collateralization_ratio_by_date(self, date):
        ratio = #TODO: how to find this ratio?
        self.stats.loc[self.stats['date'] == date, 'collateralization_ratio'] = ratio


    def __str__(self):
        return 'Loan_id:{:0>2d}, current_borrowed:${:6d}, current_collateral:{}, start_date:{} ' \
               ''.format(self.id, self.current_borrowed_cad, self.current_collateral, self.start_date)


def set_test_mode(test_case):
    global TEST_MODE
    TEST_MODE = test_case


def set_loans_file(input_file):
    global LOANS_INPUT_FILE
    LOANS_INPUT_FILE = input_file


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
    global LOANS_INPUT_FILE
    file = ''
    try:
        file = './tests/data/'+TEST_MODE if TEST_MODE else './data/'+LOANS_INPUT_FILE
        print('[INFO] Initializing loans with file: '+file)
        df_loans = pd.read_csv(file)
    except FileNotFoundError:
        print('[ERROR] Could not find file [{}]'.format(file))
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
            if new_loan_entry_is_valid(active_loans, row):
                active_loans.append(instantiate_new_loan(row))
                update_collateral_records(active_loans, row)
                update_borrowed_cad_history(active_loans, row)
        if row['type'] is COLLATERAL_INCREASED or row['type'] is COLLATERAL_DECREASED:
            update_collateral_records(active_loans, row)
        if row['type'] is CAD_BORROWED_INCREASED:
            update_borrowed_cad_history(active_loans, row)
    return active_loans


def new_loan_entry_is_valid(active_loans, csv_entry):
    for cdp in active_loans:
        if csv_entry['wallet_address'] == cdp.wallet_address:
            raise InvalidLoanData('Trying to create a loan that already exists.')
    return True


def instantiate_new_loan(entry):
    return Loan(entry['start_date'], entry['wallet_address'])


def update_collateral_records(loans, csv_entry):
    for cdp in loans:
        if cdp.wallet_address == csv_entry['wallet_address']:
            new_entry = {pd.Timestamp(csv_entry['date_update']): {'type': csv_entry['type'],
                                                                  'amount': csv_entry['collateral_amount']}}
            cdp.collateral_history.update(new_entry)
            if csv_entry['type'] is COLLATERAL_DECREASED:
                cdp.current_collateral -= csv_entry['collateral_amount']
            else:
                cdp.current_collateral += csv_entry['collateral_amount']


def update_borrowed_cad_history(loans, csv_entry):
    for cdp in loans:
        if cdp.wallet_address == csv_entry['wallet_address']:
            cdp.borrowed_cad_history.update({pd.Timestamp(csv_entry['date_update']): csv_entry['cad_borrowed']})
            cdp.current_borrowed_cad += csv_entry['cad_borrowed']


def update_ratios_to_current_price(price_given=0):
    date = tools.get_current_date_for_exchange_api()
    price = price_given if price_given else tools.get_usd_price()
    for cdp in Loan.active_loans: cdp.update_stats_entry(date, price)