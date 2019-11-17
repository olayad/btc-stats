#!/usr/bin/env python3

import pandas as pd
from tools import get_price, update_loan_ratio
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go


app = dash.Dash()

try:
    df = pd.read_csv('./data/cdp.csv')
except FileNotFoundError:
    print('ERROR - Loan data (cdp.csv) file not found, exiting program')
    exit(1)

df.set_index('num', inplace=True)
print(df.head())


# curr_price = get_price()

app.layout = html.Div([
    html.H1(id='btc-price', children='BTC: USD.'),
    dcc.Interval(id='update_interval', interval=10000, n_intervals=0),
    html.Div(children='what a steal')
])


@app.callback(Output('btc-price', 'children'),
              [Input('update_interval', 'n_intervals')])
def update_stats(n_intervals):
    global df
    print('\n updating stats...')
    curr_price = get_price()
    # update_loan_ratio(df, curr_price)
    return 'BTC: '+str(curr_price)+' USD'

if __name__ == '__main__':
    app.run_server()