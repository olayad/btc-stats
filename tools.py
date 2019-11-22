import requests
import json
import sys
from exceptions import ThirdPartyApiUnavailable

def get_price():
    price = {}
    usd_price = call_exchange_api()

    # cad_price = round(usd_price / fx_rate, 1)
    # price.update({'USD': usd_price, 'CAD': cad_price})
    # TODO: need to fix what returns below
    return price


def call_exchange_api():
    bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'
    response = None
    try:
        response = requests.get(bitfinex_url)
    except TimeoutError as ex:
        print('[ERROR] Bitfinex API unavailable, terminating program.', ex)
        # TODO: show user message error before terminating program
        sys.exit(1)
    return json.loads(response.text)[0][1]


def get_cadusd_rates(start_date):
    json_response = call_fx_api(start_date)
    fill_missing_weekend_rates(json_response)
    return [i['FXCADUSD']['v'] for i in json_response['observations']]


def call_fx_api(start_date):
    bankofcanada_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?start_date='+start_date
    response = None
    try:
        response = requests.get(bankofcanada_url, timeout=1)
    except TimeoutError as ex:
        print("[ERROR] Bank of Canada API unavailable, terminating program.", ex)
        # TODO: show user message error before terminating program
        sys.exit(1)
    return json.loads(response.text)

def fill_missing_weekend_rates(data):
    # Bitcoin never closes its branch, so need to make up for banks missing data
    print(data['observations'])
    for i in data['observations']:
        print(i)