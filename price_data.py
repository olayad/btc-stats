import pandas as pd
from exceptions import InitializationDataNotFound
from tools import update_btcusd_csv


class PriceData:

    def __init__(self):
        self.df_btcusd = self.load_price_dataframe()

    def load_price_dataframe(self):
        update_btcusd_csv()
        try:
            self.df_btcusd = pd.read_csv('./data/btcusd.csv')
        except FileNotFoundError:
            print('[ERROR] Could not find file [/data/btcusd.csv].')
            raise InitializationDataNotFound
        self.df_btcusd['Date'] = pd.to_datetime(self.df_btcusd['Date'])
        self.df_btcusd['Last'] = pd.to_numeric(self.df_btcusd['Close'])
        return self.df_btcusd
