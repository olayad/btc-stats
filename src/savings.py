#!/usr/bin/env/ python3

import pandas as pd
import config as cfg
from exceptions import InitializationDataNotFound, InvalidData
from price_data import PriceData

df_btcusd = PriceData().df_btcusd


class Savings:
    account_input_df = None
    rates_input_df = None
    account_balance_history_btc = {}    # {date: amount}
    balance_btc = 0
    stats = pd.DataFrame()


def init_savings(rates_file='rates.csv'):
    Savings.account_input_df, Savings.rates_input_df = load_input_file(rates_file)
    get_total_savings_btc()
    calculate_stats()
    # TODO: order savings_df by column date
    # TODO: order interest_df by column date


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
    return savings_input_df, rates_input_df


def get_total_savings_btc():
    for index, row in Savings.account_input_df.iterrows():
        if row['amount_btc'] < 0: raise InvalidData
        if row['type'] is cfg.INCREASE:
            Savings.balance_btc += row['amount_btc']
            Savings.account_balance_history_btc.update({pd.Timestamp(row['date']): row['amount_btc']})
        if row['type'] is cfg.DECREASE:
            Savings.balance_btc -= row['amount_btc']
            Savings.account_balance_history_btc.update({pd.Timestamp(row['date']): -row['amount_btc']})

    print(f'account_balance_history_btc:{Savings.account_balance_history_btc}')


def calculate_stats():
    account_start_date = Savings.account_input_df["date"].iloc[0]
    Savings.stats['date'] = df_btcusd[df_btcusd['Date'] >= account_start_date]['Date']
    Savings.stats['balance_btc'] = populate_balances_btc()

    # print(df_btcusd.head())
    print(f'account start date: {Savings.account_input_df["date"].iloc[0]}')
    print(f'\n***Savings stats***')
    print(Savings.stats)


def populate_balances_btc():
    balance_btc_df = []
    dates_which_had_balance_update = list(Savings.account_balance_history_btc.keys())
    curr_balance = Savings.balance_btc
    print(f'Savings.balance_btc:{Savings.balance_btc}')
    for index, row in Savings.stats.iterrows():
        if row['date'] in dates_which_had_balance_update:
            print(f'date in list, {row["date"]}, {Savings.account_balance_history_btc[row["date"]]} ')
            if Savings.account_balance_history_btc[row['date']] > 0:
                curr_balance += Savings.account_balance_history_btc[row['date']]
            else:
                curr_balance -= Savings.account_balance_history_btc[row['date']]
            balance_btc_df.append(curr_balance)
        else:
            balance_btc_df.append(curr_balance)
    print(f'balance_btc_df:{balance_btc_df}')
    return balance_btc_df
