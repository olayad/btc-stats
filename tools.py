import requests
import json


def get_price():
    price = {}
    bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'
    response = requests.get(bitfinex_url)
    json_response = json.loads(response.text)
    usd_price = json_response[0][1]

    # cad_price = round(usd_price / fx_rate, 1)
    # price.update({'USD': usd_price, 'CAD': cad_price})
    # TODO: need to fix what returns below
    return price


def get_cadusd_rates(start_date):
    bankofcanada_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?start_date='+start_date
    response = requests.get(bankofcanada_url)
    json_response = json.loads(response.text)
    # fx_rate = float(json_response['observations'][0]['FXCADUSD']['v'])
    # print('\n\nget_cadusd_rate response')
    # print(json_response)
    # print()
    # for item in json_response['observations']:
    #     print(item['FXCADUSD']['v'])
    fill_rates_weekend_data(json_response)

    return [i['FXCADUSD']['v'] for i in json_response['observations']]
    # print(json_response['observations'])

def fill_rates_weekend_data(data):
    print(data['observations'])
    for i in data['observations']:
        print(i)
        # TODO: complete this