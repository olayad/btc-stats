import requests
import json

bitfinex_url = 'https://api-pub.bitfinex.com/v2/tickers?symbols=tBTCUSD'

def get_price():
    response = requests.get(bitfinex_url)
    json_response = json.loads(response.text)
    curr_price = json_response[0][1]
    print('new price is:{}'.format(curr_price))
    return curr_price

def update_loan_ratio(df, curr_price):
    ratio = []
    for i in df.index:
        print(type(i))
        print(df.iloc('i'))
        # print('i:{}', i['amount'])
        break