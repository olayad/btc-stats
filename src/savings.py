#!/usr/bin/env/ python3

import pandas as pd
import itertools
# import datetime
import config as cfg
# import tools
from exceptions import InitializationDataNotFound, InvalidData
# from price_data import PriceData

class Savings:
    savings_df = None
    rates_df = None
    total_btc = 0
    # interest_history_cad = {pd.Timestamp('2020-06-01'): 4.1}


def init_savings(rates_file='rates.csv'):
    Savings.savings_df, Savings.rates_df = load_input_file(rates_file)
    get_total_savings_btc()


def load_input_file(rates_file):
    savings_file = ''
    print('[INFO] Initializing savings with files: ' + savings_file + ' - ' + rates_file)
    try:
        savings_file = './data/'+cfg.TEST_MODE if cfg.TEST_MODE else cfg.SAVINGS_INPUT_FILE
        rates_file = './data/'+rates_file
        savings_df = pd.read_csv(savings_file)
        rates_df = pd.read_csv(rates_file)
    except FileNotFoundError as e:
        print(f'[ERROR] Please check files exist: [{savings_file}, {rates_file}], {e}')
        raise InitializationDataNotFound
    savings_df.set_index('id', inplace=True)
    rates_df.set_index('id', inplace=True)
    return savings_df, rates_df


def get_total_savings_btc():
    for index, row in Savings.savings_df.iterrows():
        if row['amount_btc'] < 0 : raise InvalidData
        if row['type'] is cfg.INCREASE:
            Savings.total_btc += row['amount_btc']
        if row['type'] is cfg.DECREASE:
            Savings.total_btc -= row['amount_btc']




