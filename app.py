#!/usr/bin/env python3

from datetime import datetime, timedelta
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from loan import get_loans, set_test_mode
from exceptions import InitializationDataNotFound, ThirdPartyApiUnavailable
import sys
import argparse
import tools

loans = None

parser = argparse.ArgumentParser(description='CDP stats server.')
parser.add_argument('-t', '--test', help='Specify the test suite (loans[x].csv file to run')
args = parser.parse_args()

if args.test:
    set_test_mode(args.test)

try:
    loans = get_loans()
except InitializationDataNotFound:
    print('[ERROR] Validate \'loan.csv\' and \'btcusd.csv\' files are available' +
          ' in \'/data/\' dir. Terminating execution.')
    sys.exit(1)
except ThirdPartyApiUnavailable:
    print('[ERROR] Third party API not responding, try again later. Terminating execution.')
    sys.exit(1)




app = dash.Dash()
app.layout = html.Div([
    # Price ticker
    html.H1(id='btc_price', children='BTC: USD.'),
    dcc.Interval(id='update_interval', interval=10000, n_intervals=0),

    # Time frame selection
    html.Div([
        html.Div([
            html.Label(children='Select time frame:')
        ], style={'width': '150px', 'display': 'inline-block', 'vertical-align': 'middle'}),
        html.Div([
            dcc.Dropdown(id='days_dropbox',
                options=[
                    {'label': '90 days', 'value': 90},
                    {'label': '60 days', 'value': 60},
                    {'label': '30 days', 'value': 30}
                ],
                value=60)
        ], style={'width': '150px', 'display': 'inline-block', 'vertical-align': 'top'})
    ], style={'padding-top': '20px'}),

    html.Div([
        dcc.Graph(id='ratio_graph')
    ])
])

@app.callback(Output('btc_price', 'children'),
              [Input('update_interval', 'n_intervals')])
def update_btc_price(n_intervals):
    price = tools.get_usd_price()
    return 'BTC: '+str(price['USD'])+' USD - '+str(price['CAD'])+' CAD'

@app.callback(Output('ratio_graph', 'figure'),
              [Input('days_dropbox', 'days')])
def update_graph(n_days):
    global loans
    print('active_loans from app.py:')
    print(loans.active_loans)

    # trace1 = go.Scatter(x=df_btcusd[df_btcusd['Date'] >= start_date],
    #                     y=df_cdp['coll_ratio'])



if __name__ == '__main__':


    app.run_server()
