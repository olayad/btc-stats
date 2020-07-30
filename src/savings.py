#!/usr/bin/env/ python3

import pandas as pd
# import datetime
# import itertools
#
import config as cfg
# import tools
from exceptions import InitializationDataNotFound
# from price_data import PriceData



class Savings:
    input_file_df = 0
    total_btc = 0
    interest_history_cad = {}


def init_savings():
    Savings.input_file_df = load_input_file()

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
    return Savings.total_btc

