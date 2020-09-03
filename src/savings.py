#!/usr/bin/env/ python3

from calendar import monthrange
import datetime
import collections
import pandas as pd
import config as cfg
from exceptions import InitializationDataNotFound, InvalidData
from price_data import PriceData


df_btcusd = PriceData().df_btcusd

# TODO: move to config
DECIMALS = 8
# MONTH={
#         'ALL':0,
#         'JAN':1,
#         'FEB':2,
#         'MAR':3,
#         'APR':4,
#         'MAY':5,
#         'JUN':6,
#         'JUL':7,
#         'AUG':8,
#         'SEP':9,
#         'OCT':10,
#         'NOV':11,
#         'DEC':12
# }

class Savings:
    account_input_df = None
    rates_input_df = None
    stats = pd.DataFrame()
    balance_history_btc = collections.OrderedDict()    # {date: +amount increased / -amount decreased}
    balance_btc = 0
    daily_rate_history = collections.OrderedDict()  # {date: daily interest rate}
    daily_rate = 0


def init_savings(rates_file='rates.csv'):
    Savings.account_input_df, Savings.rates_input_df = load_input_file(rates_file)
    Savings.daily_rate = load_rates()
    get_total_savings_btc()
    calculate_stats()


def load_input_file(rates_file):
    savings_file = ''
    try:
        savings_file = './data/' + cfg.TEST_MODE if cfg.TEST_MODE else cfg.SAVINGS_INPUT_FILE
        print('[INFO] Initializing savings with files: ' + savings_file + ' - ' + rates_file)
        rates_file = './data/' + rates_file
        savings_input_df = pd.read_csv(savings_file)
        rates_input_df = pd.read_csv(rates_file)
    except FileNotFoundError as e:
        print(f'[ERROR] Please check files exist: [{savings_file}, {rates_file}], {e}')
        raise InitializationDataNotFound
    savings_input_df.set_index('id', inplace=True)
    rates_input_df.set_index('id', inplace=True)
    savings_input_df.sort_values('date', ascending=True, inplace=True)
    rates_input_df.sort_values('date', ascending=True, inplace=True)

    return savings_input_df, rates_input_df


def load_rates():
    daily_interest_rate = 0
    for index, row in Savings.rates_input_df.iterrows():
        daily_interest_rate = round((row['apy']/365)/100, DECIMALS)
        Savings.daily_rate_history.update({pd.Timestamp(row['date']): daily_interest_rate})
    return daily_interest_rate


def get_total_savings_btc():
    for index, row in Savings.account_input_df.iterrows():
        if row['amount_btc'] < 0: raise InvalidData
        if row['type'] is cfg.INCREASE:
            Savings.balance_btc += row['amount_btc']
            Savings.balance_history_btc.update({pd.Timestamp(row['date']): row['amount_btc']})
        if row['type'] is cfg.DECREASE:
            Savings.balance_btc -= row['amount_btc']
            Savings.balance_history_btc.update({pd.Timestamp(row['date']): -row['amount_btc']})


def calculate_stats():
    account_start_date = Savings.account_input_df["date"].iloc[0]
    Savings.stats['date'] = df_btcusd[df_btcusd['Date'] >= account_start_date]['Date']
    Savings.stats['daily_rate'] = calculate_daily_rates()
    Savings.stats['movements_btc'] = populate_movements_btc()
    Savings.stats['balance_btc'] = calculate_balance()


def calculate_daily_rates():
    daily_rate_df = []
    dates_with_rate_update = list(Savings.daily_rate_history.keys())
    first_rate_update = list(Savings.daily_rate_history.items())[0][1]
    curr = first_rate_update
    for index, row in Savings.stats[::-1].iterrows():
        if row['date'] in dates_with_rate_update:
            curr = Savings.daily_rate_history[row['date']]
        daily_rate_df.append(curr)
    return daily_rate_df[::-1]


def populate_movements_btc():
    movements_btc_df = []
    dates_with_balance_update = list(Savings.balance_history_btc.keys())
    curr = 0
    for index, row in Savings.stats[::-1].iterrows():
        if row['date'] in dates_with_balance_update:
            curr += Savings.balance_history_btc[row['date']]
            movements_btc_df.append(Savings.balance_history_btc[row['date']])
        else:
            movements_btc_df.append(0)
    return movements_btc_df[::-1]


def calculate_balance():
    balance_btc_df = []
    curr_balance = 0
    prev_balance = 0
    for index, row in Savings.stats[::-1].iterrows():
        interest = prev_balance * row['daily_rate']
        curr_balance = round(interest + prev_balance + row['movements_btc'], DECIMALS)
        prev_balance = curr_balance
        balance_btc_df.append(curr_balance)
    return balance_btc_df[::-1]


def get_monthly_interest_gains(year=datetime.datetime.now().year, month=datetime.datetime.now().month):
    assert(0 < month < 13)
    assert(year >= datetime.datetime.now().year)
    stats = Savings.stats
    start_date = pd.Timestamp(year=year, month=month, day=1)
    end_date = pd.Timestamp(year=year, month=month, day=monthrange(year, month)[1])
    df = stats[(stats['date'] >= start_date) & (stats['date'] <= end_date)]
    movements = df['movements_btc'].sum() - df['movements_btc'].iloc[-1]
    gains = round(((df["balance_btc"].iloc[0] - df['balance_btc'].iloc[-1]) - movements), 8)
    return gains
