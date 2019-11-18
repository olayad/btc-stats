import requests
import json

bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'
bankofcanada_url = 'https://www.bankofcanada.ca/valet/observations/FXCADUSD/json?recent=1'

def get_price():
    price = {}
    response = requests.get(bitfinex_url)
    json_response = json.loads(response.text)
    usd_price = json_response[0][1]

    response = requests.get(bankofcanada_url)
    json_response = json.loads(response.text)
    fx_rate = float(json_response['observations'][0]['FXCADUSD']['v'])
    cad_price = round(usd_price / fx_rate, 1)

    price.update({'USD': usd_price, 'CAD': cad_price})
    return price

def update_loan_ratios(df, price):
    ratio = []
    for index, row in df.iterrows():
        ratio.append((price['CAD'] * row['coll_amount'])/ row['loan_amount'])
    return ratio

