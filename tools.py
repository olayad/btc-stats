import requests
import json
import sys
from exceptions import ThirdPartyApiUnavailable
import datetime

quandl_url = 'https://www.quandl.com/api/v3/datasets/BITFINEX/BTCUSD.csv?api_key=yynH4Pnq-X7AhiFsFdEa'
bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'
bankofcanada_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?'


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
    response = Noneg
    try:
        response = requests.get(bitfinex_url, timeout=2)
    except requests.exceptions.Timeout:
        print('[ERROR] Bitfinex API not responding.')
        raise ThirdPartyApiUnavailable
    return json.loads(response.text)[0][1]


def get_cadusd_rates(start_date, end_date=str(datetime.date.today())):
    print('(get_cadusd_rates) - start:{},  end:{}'.format(start_date, end_date))
    json_response = call_fx_api(start_date, end_date)
    observations = {i['d']: i['FXCADUSD']['v'] for i in json_response['observations']}
    params = {'start_date': start_date, 'end_date': end_date}
    rates = [params, observations]
    print('rates(should be list with 2 dicts):', rates)


    fill_missing_day_rates(rates)


    return [i['FXCADUSD']['v'] for i in json_response['observations']]


    # TODO: I am trying to clean up my messages in the terminal so I can elaborate an action plan on how to move forward.
    # Thinking there might be an error on how I am managing the start and end dates. Perhaps should be adding an additional 1
    # to the end date. Not sure if this is correct yet. Suppose I need 5 readings, because that is what Finex gave me. This is
    # what my master is. The number of bitcoin exchange observations and whatever Bank of Canada tries to give me, I should be
    # getting.




def call_fx_api(start_date, end_date):
    response = None
    try:
        response = requests.get(bankofcanada_url+'start_date='+start_date +
                                '&end_date='+end_date, timeout=2)
    except requests.exceptions.Timeout:
        print('[ERROR] Bank of Canada API not responding.')
        raise ThirdPartyApiUnavailable
    return json.loads(response.text)


def fill_missing_day_rates(rates):
    # Bitcoin never closes its branch, so need to make up for banks missing rates
    # data (i.e. holidays and weekends). A day is added to the end_date value
    # because the API information retrieved from Bitfinex
    start_date = datetime.datetime.strptime(rates[0]['start_date'], '%Y-%m-%d')
    end_date = datetime.datetime.strptime(rates[0]['end_date'], '%Y-%m-%d')
    requested_days = (end_date - start_date)
    # print('(fill_missing_day rates) start_date:{}, end_date:{}'.format(start_date, end_date))

    new_end_date = end_date + datetime.timedelta(days=1)
    print('new end date', new_end_date)
    new_requested_days = new_end_date - start_date

    print('API rate data len (days included in readings): {}, data:{},'
          ' original_requested_days:{}, '
          'new_requested_days:{}'.format(len(rates[1]),
                                         rates[1],
                                         requested_days,
                                         new_requested_days))



    # print(datetime.date(rates['start_date']) - datetime.date(rates['end_date']))




    sys.exit(1)