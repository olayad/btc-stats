#!/usr/bin/env python3

import pandas as pd
from tools import get_price, update_loan_ratios
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go


app = dash.Dash()

try:
    df_cdp = pd.read_csv('./data/cdp.csv')
    df_btcusd = pd.read_csv('./data/btcusd.csv')
except FileNotFoundError:
    print('ERROR - File not found, exiting program')
    exit(1)

df_cdp.set_index('num', inplace=True)
df_btcusd['Date'] = pd.to_datetime(df_btcusd['Date'])
df_btcusd['Last'] = pd.to_numeric(df_btcusd['Last'])
print(df_btcusd.head())



app.layout = html.Div([
    # Price ticker
    html.H1(id='btc-price', children='BTC: USD.'),
    dcc.Interval(id='update_interval', interval=10000, n_intervals=0),

    # Time frame selection
    html.Div([
        html.Div([
            html.Label(children='Select time frame:')
        ], style={'width': '150px', 'display': 'inline-block', 'vertical-align': 'middle'}),
        html.Div([
            dcc.Dropdown(
                options=[
                    {'label': '90 days', 'value': 90},
                    {'label': '60 days', 'value': 60},
                    {'label': '30 days', 'value': 30}
                ],
                value=60)
        ], style={'width': '150px', 'display': 'inline-block', 'vertical-align': 'top'})
    ], style={'padding-top': '20px'})

])


@app.callback(Output('btc-price', 'children'),
              [Input('update_interval', 'n_intervals')])
def update_stats(n_intervals):
    global df_cdp
    price = get_price()
    df_cdp['coll_ratio'] = update_loan_ratios(df_cdp, price)
    return 'BTC: '+str(price['USD'])+' USD - '+str(price['CAD'])+' CAD'

if __name__ == '__main__':
    app.run_server()