import requests
import json
import sys
from exceptions import BitfinexApiUnavailable, BankOfCanadaApiUnavailable,\
    QuandlApiUnavailable


bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'
bankofcanada_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?start_date='


def get_price():
    price = {}
    usd_price = call_exchange_api()

    # TODO: need to fix what returns below
    return price


def call_exchange_api():
    response = None
    try:
        response = requests.get(bitfinex_url)
    except requests.exceptions.Timeout:
        raise BitfinexApiUnavailable
    return json.loads(response.text)[0][1]


def get_cadusd_rates(start_date):
    json_response = call_fx_api(start_date)
    fill_missing_weekend_rates(json_response)
    return [i['FXCADUSD']['v'] for i in json_response['observations']]


def call_fx_api(start_date):
    response = None
    try:
        response = requests.get(bankofcanada_url+start_date, timeout=1)
    except requests.exceptions.Timeout:
        raise BankOfCanadaApiUnavailable
    return json.loads(response.text)

def fill_missing_weekend_rates(data):
    # Bitcoin never closes its branch, so need to make up for banks missing data
    print(data['observations'])
    for i in data['observations']:
        print(i)