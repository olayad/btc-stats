#!/usr/bin/env/ python3

import pandas as pd
import itertools
# import datetime
import config as cfg
# import tools
from exceptions import InitializationDataNotFound, InvalidData
# from price_data import PriceData




class Savings:
    input_file_df = None
    total_btc = 0
    interest_history_cad = {}


def init_savings():
    Savings.input_file_df = load_input_file()
    get_total_btc()


def load_input_file():
    file = ''
    try:
        file = './data/'+cfg.TEST_MODE if cfg.TEST_MODE else cfg.SAVINGS_INPUT_FILE
        print('[INFO] Initializing savings with file: '+file)
        df = pd.read_csv(file)
    except FileNotFoundError:
        print('[ERROR] Could not find file [{}]'.format(file))
        raise InitializationDataNotFound
    df.set_index('num', inplace=True)
    return df


def get_total_btc():
    for index, row in Savings.input_file_df.iterrows():
        if row['amount_btc'] < 0 : raise InvalidData
        if row['type'] is cfg.INCREASE:
            Savings.total_btc += row['amount_btc']
        if row['type'] is cfg.DECREASE:
            Savings.total_btc -= row['amount_btc']




