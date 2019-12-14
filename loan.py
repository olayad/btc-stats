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
DAILY_INTEREST = 0.000329

class Loan:
    counter = 1
    active_loans = []
    df_loans = None
    df_btcusd = None
    df_debt = None

    def __init__(self, start_date, wallet_address):
        self.stats = pd.DataFrame()
        self.collateral_history = {}    # {date:{'type': _ , 'amount': _}
        self.debt_history_cad = {}  # {date: amount}
        self.current_collateral = 0
        self.current_debt_cad = 0
        self.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        self.wallet_address = wallet_address
        self.id = self.counter
        Loan.counter += 1

    def calculate_loan_stats(self):
        loan_start_date = pd.Timestamp(self.start_date)
        self.stats['date'] = Loan.df_btcusd[Loan.df_btcusd['Date'] >= loan_start_date]['Date']
        self.stats['btc_price_usd'] = Loan.df_btcusd[Loan.df_btcusd['Date'] >= loan_start_date]['Last']
        self.stats['fx_cadusd'] = tools.get_fx_cadusd_rates(str(self.start_date))
        self.stats['btc_price_cad'] = [round(row['btc_price_usd'] / float(row['fx_cadusd']), 1) for _, row in self.stats.iterrows()]
        self.stats['debt_cad'] = self.populate_debt_cad()
        self.stats['collateral_amount'] = self.populate_collateral_amounts()
        self.stats['collateralization_ratio'] = self.calculate_collateralization_ratio()
        self.stats['interest_cad'] = self.calculate_interest()

    def populate_debt_cad(self):
        borrowed_cad_values = []
        dates_which_had_borrowed_cad_update = list(self.debt_history_cad.keys())
        curr_borrowed = self.current_debt_cad
        for index, row in self.stats.iterrows():
            borrowed_cad_values.append(curr_borrowed)
            if row['date'] in dates_which_had_borrowed_cad_update:
                curr_borrowed -= self.debt_history_cad[row['date']]
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
        for _, row in self.stats.iterrows():
            ratio = round((row['btc_price_cad'] * row['collateral_amount']) / row['debt_cad'], 2)
            ratio_values.append(ratio)
        return ratio_values

    def calculate_interest(self):
        df_interest = []
        start_date = datetime.datetime(self.start_date.year, self.start_date.month, self.start_date.day)
        interest = 0
        for _, row in self.stats[::-1].iterrows():
            daily_interest = DAILY_INTEREST * row['debt_cad']
            interest += daily_interest
            df_interest.insert(0, round(interest, 2))
        return df_interest

    def update_stats_with_current_price(self, date_to_update, btc_price_usd):
        if self.date_to_update_is_not_in_stats(date_to_update):
            self.append_new_row_to_stats(date_to_update, btc_price_usd)
        else:
            self.update_row_prices(date_to_update, btc_price_usd)
            self.update_row_ratio(date_to_update, btc_price_usd)

    def date_to_update_is_not_in_stats(self, date_to_update):
        df_earliest_date = self.stats.iloc[0]['date']
        return df_earliest_date != date_to_update

    def append_new_row_to_stats(self, date_to_update, btc_price_usd):
        fx_rate = float(tools.get_fx_cadusd_rates(datetime.datetime.now().strftime('%Y-%m-%d'))[0])
        btc_price_cad = round(btc_price_usd / fx_rate, 1)
        ratio = (btc_price_cad * self.current_collateral) / self.current_debt_cad
        interest = self.calculate_new_row_interest()
        new_row = pd.DataFrame({'date': [date_to_update],
                                'btc_price_usd': [btc_price_usd],
                                'fx_cadusd': [fx_rate],
                                'btc_price_cad': [btc_price_cad],
                                'debt_cad': [self.current_debt_cad],
                                'collateral_amount': [self.current_collateral],
                                'collateralization_ratio': [ratio],
                                'interest_cad': [interest]})
        self.stats = pd.concat([new_row, self.stats]).reset_index(drop=True)

    def update_row_prices(self, date_to_update, btc_price_usd):
        fx_rate = float(tools.get_fx_cadusd_rates(datetime.datetime.now().strftime('%Y-%m-%d'))[0])
        btc_price_cad = round(btc_price_usd / fx_rate, 1)
        self.stats.loc[self.stats['date'] == date_to_update, 'fx_cadusd'] = fx_rate
        self.stats.loc[self.stats['date'] == date_to_update, 'btc_price_usd'] = btc_price_usd
        self.stats.loc[self.stats['date'] == date_to_update, 'btc_price_cad'] = btc_price_cad
        # print('updated stats with cad_price:\n{}'.format(btc_price_cad))


    def update_row_ratio(self, date_to_update, btc_price_usd):
        btc_price_cad = self.stats.loc[self.stats['date'] == date_to_update, 'btc_price_cad']
        collateral_amount = self.stats.loc[self.stats['date'] == date_to_update, 'collateral_amount']
        debt_cad = self.stats.loc[self.stats['date'] == date_to_update, 'debt_cad']
        current_ratio = round((btc_price_cad * collateral_amount) / debt_cad, 2)
        self.stats.loc[self.stats['date'] == date_to_update, 'collateralization_ratio'] = current_ratio

    def calculate_new_row_interest(self):
        interest_accumulated = self.stats.iloc[0]['interest_cad']
        return round(interest_accumulated + (DAILY_INTEREST * self.current_debt_cad), 2)

    def __str__(self):
        return 'Loan_id:{:0>2d}, current_debt:${:6d}, current_collateral:{}, start_date:{} ' \
               ''.format(self.id, self.current_debt_cad, self.current_collateral, self.start_date)


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
    Loan.df_debt = build_debt_dataframe()


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
            raise InvalidLoanData('Trying to create a loan that already '
                                  'exists:{}'.format(cdp.wallet_address))
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
            cdp.debt_history_cad.update({pd.Timestamp(csv_entry['date_update']): csv_entry['debt_cad']})
            cdp.current_debt_cad += csv_entry['debt_cad']


def update_loans_with_current_price(date_given=0, price_given=0):
    date = tools.get_current_date_for_exchange_api() if not date_given else date_given
    price = price_given if price_given else tools.get_usd_price()
    for cdp in Loan.active_loans: cdp.update_stats_with_current_price(pd.Timestamp(date), float(price))


def build_debt_dataframe():
    btc_cad_price = []
    interest_cad = []
    debt = []
    dates = []
    oldest_active_loan_date = pd.to_datetime(find_oldest_active_date())
    most_recent_day_in_stats = Loan.active_loans[0].stats.iloc[0]['date']
    curr_date = most_recent_day_in_stats
    loans_generating_interest_at_date = get_loans_generating_interest_at_date(curr_date)
    while curr_date != (oldest_active_loan_date - datetime.timedelta(days=1)):
        borrowed_sum = interest_sum = 0
        for cdp in loans_generating_interest_at_date:
            borrowed_sum += cdp.stats[cdp.stats['date'] == curr_date]['debt_cad'].values[0]
            interest_sum += cdp.stats[cdp.stats['date'] == curr_date]['interest_cad'].values[0]
        dates.append(curr_date)
        interest_cad.append(round(interest_sum, 2))
        debt.append(round(borrowed_sum, 2))
        curr_date -= datetime.timedelta(days=1)
        loans_generating_interest_at_date = get_loans_generating_interest_at_date(curr_date)
    df_debt = pd.DataFrame({'date': dates,
                            'btc_price_cad': get_btc_cad_price_data_from_oldest_loan(),
                            'debt_cad': debt,
                            'interest_cad': interest_cad})
    df_debt['total_liab_cad'] = calculate_total_liabilities_cad(df_debt)
    df_debt['interest_btc'] = calculate_interest_in_btc(df_debt)
    df_debt['debt_btc'] = calculate_debt_in_btc(df_debt)
    df_debt['total_liab_btc'] = calculate_total_liabilities_btc(df_debt)
    return df_debt


def find_oldest_active_date():
    oldest_active = datetime.datetime.today().date()
    for cdp in Loan.active_loans:
        if cdp.start_date < oldest_active: oldest_active = cdp.start_date
    return oldest_active


def get_loans_generating_interest_at_date(date):
    loans_active_at_date = []
    for cdp in Loan.active_loans:
        if cdp.start_date <= date: loans_active_at_date.append(cdp)
    return loans_active_at_date


def get_btc_cad_price_data_from_oldest_loan():
    btc_cad_price = []
    oldest_active = find_oldest_active_date()
    for cdp in Loan.active_loans:
        if cdp.start_date == oldest_active: btc_cad_price = cdp.stats['btc_price_cad']
    return btc_cad_price


def calculate_total_liabilities_cad(df_debt):
    liabilities_cad = []
    for _, row in df_debt.iterrows():
        liabilities_cad.append(round((row['debt_cad'] + row['interest_cad']), 4))
    return liabilities_cad


def calculate_interest_in_btc(df_debt):
    interest_btc = []
    for _, row in df_debt.iterrows():
        interest_btc.append(round((row['interest_cad'] / row['btc_price_cad']), 4))
    return interest_btc


def calculate_debt_in_btc(df_debt):
    debt_btc = []
    for _, row in df_debt.iterrows():
        debt_btc.append(round((row['debt_cad'] / row['btc_price_cad']), 4))
        # print('debt_cad:{}, btc_price:{}, debt_btc:{}'.format(row['debt_cad'], row['btc_price_cad'], (row['debt_cad'] / row['btc_price_cad'])))
    return debt_btc


def calculate_total_liabilities_btc(df_debt):
    liabilities_btc = []
    for _, row in df_debt.iterrows():
        liabilities_btc.append(round((row['debt_btc'] + row['interest_btc']), 4))
    return liabilities_btc


def update_debt_df_with_current_price():
    Loan.df_debt['btc_price_cad'] = get_btc_cad_price_data_from_oldest_loan()
    Loan.df_debt['debt_btc'] = calculate_debt_in_btc(Loan.df_debt)
    Loan.df_debt['interest_btc'] = calculate_interest_in_btc(Loan.df_debt)
    Loan.df_debt['total_liab_btc'] = calculate_total_liabilities_btc(Loan.df_debt)
    # print(Loan.active_loans[0].stats.head())
    # print('new_debt after price update\n', Loan.df_debt.head())
    # print()
    # print()