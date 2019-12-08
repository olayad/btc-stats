#!/usr/bin/env python3

# from datetime import datetime, timedelta, date
import datetime
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from loan import Loan, get_loans, set_test_mode, set_loans_file, update_ratios_with_current_price
from exceptions import InitializationDataNotFound, ThirdPartyApiUnavailable, InvalidLoanData
import sys
import argparse
import tools

loans = None

parser = argparse.ArgumentParser(description='CDP stats server.')

parser.add_argument('-t', '--test', help='Specify the test suite (/tests/data/[loans-x].csv file to run')
parser.add_argument('-f', '--file', help='Specify the \'/data/[loans].csv\' file to run')

args = parser.parse_args()
if args.test:
    set_test_mode(args.test)
if args.file:
    set_loans_file(args.file)

try:
    loans = get_loans()
except InitializationDataNotFound:
    print('[ERROR] Validate \'loan.csv\' and \'btcusd.csv\' files are available' +
          ' in \'/data/\' dir. Terminating execution.')
    sys.exit(1)
except ThirdPartyApiUnavailable:
    print('[ERROR] Third party API not responding, try again later. Terminating execution.')
    sys.exit(1)
except InvalidLoanData:
    print('[ERROR] /data/loan.csv file has inconsistent values (duplicate loan entry?)')


app = dash.Dash()
app.layout = html.Div([
    # Price ticker
    dcc.Interval(id='interval-component', interval=10000, n_intervals=0),

    html.H1(id='btc_price', children=''),

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
                value=30)
        ], style={'width': '150px', 'display': 'inline-block', 'vertical-align': 'top'})
    ], style={'padding-top': '20px'}),

    html.Div([
        dcc.Graph(id='ratio_graph')
    ])
])


@app.callback([Output('btc_price', 'children'),
               Output('ratio_graph', 'figure')],
              [Input('interval-component', 'n_intervals')])
def interval_update_triggered(n_intervals):
    # TODO: Need to wrap this, to catch Third Party API exception
    price = update_price()
    figure = update_collateralization_graph()
    return price, figure


def update_price():
    return 'BTC: '+str(tools.get_usd_price())+' USD'


def update_collateralization_graph():
    print('calling update_collateralization_graph')
    update_ratios_with_current_price()
    figure = build_collateralization_graph()
    return figure


def build_collateralization_graph():
    print('building graph...')
    data = []
    oldest_start_date = datetime.date.today()
    for loan in Loan.active_loans:
        if loan.start_date < oldest_start_date : oldest_start_date = loan.start_date
        trace = go.Scatter(x=loan.stats['date'],
                           y=loan.stats['collateralization_ratio'],
                           mode='lines',
                           name='$'+str(loan.current_borrowed_cad))
        data.append(trace)
    layout = go.Layout(title='Collateralization Ratio',
                       shapes=[{'type': 'line',
                                'y0': 2, 'x0': oldest_start_date,
                                'y1': 2, 'x1': datetime.date.today(),
                                'line': {'color': 'red', 'width': 1.0, 'dash': 'dot'}}],
                       legend_orientation='h',
                       showlegend=True)
    figure = {'data': data, 'layout': layout}
    return figure

if __name__ == '__main__':
    app.run_server()
