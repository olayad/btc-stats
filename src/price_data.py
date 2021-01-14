from exceptions import InitializationDataNotFound
from tools import update_btcusd_csv
import config as cfg
import pandas as pd


class PriceData:
    def __init__(self):
        self.df_btcusd = load_input_file()
        print(self.df_btcusd)


def load_input_file():
    update_btcusd_csv()
    try:
        df_btcusd = pd.read_csv(cfg.BTCUSD_INPUT_FILE)
    except FileNotFoundError:
        print(f'[ERROR] Could not find file btcusd.csv file - {cfg.BTCUSD_INPUT_FILE}.')
        raise InitializationDataNotFound
    df_btcusd['Date'] = pd.to_datetime(df_btcusd['Date'])
    df_btcusd['Last'] = pd.to_numeric(df_btcusd['Close'])
    return df_btcusd
