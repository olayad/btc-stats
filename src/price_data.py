import pandas as pd

from exceptions import InitializationDataNotFound
from tools import update_btcusd_csv


class PriceData:
    def __init__(self):
        self.df_btcusd = load_input_file()


def load_input_file():
    update_btcusd_csv()
    try:
        df_btcusd = pd.read_csv('../data/btcusd.csv')
    except FileNotFoundError:
        print('[ERROR] Could not find file [/data/btcusd.csv].')
        raise InitializationDataNotFound
    df_btcusd['Date'] = pd.to_datetime(df_btcusd['Date'])
    # df_btcusd['Last'] = pd.to_numeric(df_btcusd['Close'])
    df_btcusd['Last'] = pd.to_numeric(df_btcusd['Last'])
    return df_btcusd
