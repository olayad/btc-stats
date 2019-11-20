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
    return price

def get_cadusd_rate(start_date):
    bankofcanada_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?start_date='+start_date
    response = requests.get(bankofcanada_url)
    json_response = json.loads(response.text)
    # fx_rate = float(json_response['observations'][0]['FXCADUSD']['v'])
    print(json_response)

def update_loan_ratios(df, price):
    ratio = []
    for index, row in df.iterrows():
        ratio.append((price['CAD'] * row['coll_amount'])/ row['loan_amount'])
    return ratio

