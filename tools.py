import requests
import json
import sys
from exceptions import ThirdPartyApiUnavailable


quandl_url = 'https://www.quandl.com/api/v3/datasets/BITFINEX/BTCUSD.csv?api_key=yynH4Pnq-X7AhiFsFdEa'
bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'
bankofcanada_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?start_date='


def update_btcusd_data():
    try:
        data = requests.get(quandl_url, timeout=2)
    except requests.exceptions.Timeout:
        print('[ERROR] Quandl API not responding.')
        raise ThirdPartyApiUnavailable
    open('./data/btcusd.csv', 'wb+').write(data.content)

def get_price():
    price = {}
    usd_price = call_exchange_api()

    # TODO: need to fix what returns below
    return price


def call_exchange_api():
    response = None
    try:
        response = requests.get(bitfinex_url, timeout=2)
    except requests.exceptions.Timeout:
        print('[ERROR] Bitfinex API not responding.')
        raise ThirdPartyApiUnavailable
    return json.loads(response.text)[0][1]


def get_cadusd_rates(start_date):
    json_response = call_fx_api(start_date)
    fill_missing_weekend_rates(json_response)
    return [i['FXCADUSD']['v'] for i in json_response['observations']]


def call_fx_api(start_date):
    response = None
    try:
        response = requests.get(bankofcanada_url+start_date, timeout=2)
    except requests.exceptions.Timeout:
        print('[ERROR] Bank of Canada API not responding.')
        raise ThirdPartyApiUnavailable
    return json.loads(response.text)


def fill_missing_weekend_rates(data):
    # Bitcoin never closes its branch, so need to make up for banks missing data
    print(data['observations'])
    for i in data['observations']:
        print(i)