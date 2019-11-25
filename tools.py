import requests
import json
import sys
from exceptions import ThirdPartyApiUnavailable
import datetime

quandl_url = 'https://www.quandl.com/api/v3/datasets/BITFINEX/BTCUSD.csv?api_key=yynH4Pnq-X7AhiFsFdEa'
bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'
bankofcanada_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?'

AVG_FXCADUSD = 0.753    # Last updated Nov 23, 2019


def update_btcusd_csv():
    try:
        data = requests.get(quandl_url, timeout=2)
    except requests.exceptions.Timeout:
        print('[ERROR] Quandl API not responding.')
        raise ThirdPartyApiUnavailable
    open('./data/btcusd.csv', 'wb+').write(data.content)

def get_usd_price():
    price = call_exchange_api()
    print('get_usd_price():', price)
    return price


def call_exchange_api():
    response = None
    try:
        response = requests.get(bitfinex_url, timeout=2)
    except requests.exceptions.Timeout:
        print('[ERROR] Bitfinex API not responding.')
        raise ThirdPartyApiUnavailable
    return json.loads(response.text)[0][1]


def get_cadusd_rates(start_date, end_date=str(datetime.date.today())):
    json_response = call_fx_api(start_date, end_date)

    observations = {}
    if payload_is_not_empty(json_response):
        observations = strip_payload(json_response)
    api_data = [{'start_date': start_date, 'end_date': end_date}, observations]

    rates = fill_missing_day_rates(api_data)
    return rates


def call_fx_api(start_date, end_date):
    response = None
    try:
        response = requests.get(bankofcanada_url+'start_date='+start_date +
                                '&end_date='+end_date, timeout=2)
    except requests.exceptions.Timeout:
        print('[ERROR] Bank of Canada API not responding.')
        raise ThirdPartyApiUnavailable
    return json.loads(response.text)


def payload_is_not_empty(payload):
    return len(payload['observations']) != 0


def strip_payload(payload):
    return {i['d']: i['FXCADUSD']['v'] for i in payload['observations']}


def fill_missing_day_rates(rates):
    # Bitcoin never closes its branch, so need to make up for banks missing rates
    # data (i.e. holidays and weekends).
    # For weekdays, Bank of Canada will have a matching entry with corresponding rate.
    # For this scenario, the data given is appended to result.
    # When an entry is missing from the Bank of Canada response (holiday/weekend),
    # the algorithm will use the last previous rate added to result.
    # For edge case where the date range requested is only all holidays or weekends,
    # a global FX rate is used (updated manually).
    global AVG_FXCADUSD

    start_date = datetime.datetime.strptime(rates[0]['start_date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(rates[0]['end_date'], '%Y-%m-%d')
    result = []
    curr = start_date
    result_has_data = False
    while True:
        if curr.strftime('%Y-%m-%d') in rates[1].keys():
            result.append(rates[1][curr.strftime('%Y-%m-%d')])
            result_has_data = True
        else:  # FX shows no day data, duplicate last observation or use avg.
            result.append(result[-1]) if result_has_data else result.append(AVG_FXCADUSD)
        curr = curr + datetime.timedelta(days=1)
        if curr > end_date:
            break
    return result


