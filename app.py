#!/usr/bin/env python3

# from datetime import datetime, timedelta, date
import datetime
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from loan import Loan, get_loans, set_test_mode, set_loans_file,\
    update_loans_with_current_price
from debt import Debt
from exceptions import InitializationDataNotFound, ThirdPartyApiUnavailable, InvalidLoanData
import sys
import argparse
import tools

loans = None
# df_debt = None

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
    # df_debt = build_dataframe()
except InitializationDataNotFound:
    print('[ERROR] Validate \'loan.csv\' and \'btcusd.csv\' files are available' +
          ' in \'/data/\' dir. Terminating execution.')
    sys.exit(1)
except ThirdPartyApiUnavailable:
    print('[ERROR] Third party API not responding, try again later. Terminating execution.')
    sys.exit(1)
except InvalidLoanData:
    print('[ERROR] /data/loan.csv file has inconsistent values (duplicate loan entry?)')

debt = Debt()
debt.build_dataframe()


app = dash.Dash()
app.layout = html.Div([
    dcc.Interval(id='interval_price', interval=10000, n_intervals=0),
    dcc.Interval(id='interval_debt', interval=100000, n_intervals=0),

    html.H1(id='btc_price', children=''),

    html.Div([
        dcc.Graph(id='graph_ratio')
    ]),

    html.Div([
        html.Div([
            dcc.Graph(id='graph_debt_btc')
        ], style={'width': '50%', 'display': 'inline-block'}),

        html.Div([
            dcc.Graph(id='graph_debt_cad')
        ], style={'width': '50%', 'display': 'inline-block'})
    ])

])


@app.callback([Output('graph_debt_btc', 'figure'),
               Output('graph_debt_cad', 'figure')],
              [Input('interval_debt', 'n_intervals')])
def interval_debt_triggered(n_intervals):
    debt.update_debt_df_with_current_price()
    figure_btc = update_graph_debt_btc()
    figure_cad = update_graph_debt_cad()
    return figure_btc, figure_cad


def update_graph_debt_btc():
    trace1 = go.Scatter(x=debt.df_debt['date'],
                        y=debt.df_debt['debt_btc'],
                        mode='lines',
                        name='Debt')
    trace2 = go.Scatter(x=debt.df_debt['date'],
                        y=debt.df_debt['interest_btc'],
                        mode='lines',
                        name='Interest')
    trace3 = go.Scatter(x=debt.df_debt['date'],
                        y=debt.df_debt['total_liab_btc'],
                        mode='lines',
                        name='Total Liabilities')
    data = [trace1, trace2, trace3]
    layout = go.Layout(title='Liabilities (BTC)',
                       legend_orientation='h',
                       showlegend=True,
                       yaxis_title="BTC",
                       xaxis={
                             'rangeselector': {'buttons': [
                                 {
                                     "count": 3,
                                     "label": "3 mo",
                                     "step": "month",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 6,
                                     "label": "6 mo",
                                     "step": "month",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 1,
                                     "label": "1 yr",
                                     "step": "year",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 1,
                                     "label": "YTD",
                                     "step": "year",
                                     "stepmode": "todate"
                                 },
                                 {"step": "all"}
                             ]},
                             'rangeslider': {'visible': True},
                             'type': 'date',
                             "autorange": True
                       })
    figure = {'data': data, 'layout': layout}
    return figure


def update_graph_debt_cad():
    trace1 = go.Scatter(x=debt.df_debt['date'],
                        y=debt.df_debt['debt_cad'],
                        mode='lines',
                        name='Debt')
    trace2 = go.Scatter(x=debt.df_debt['date'],
                        y=debt.df_debt['interest_cad'],
                        mode='lines',
                        name='Interest')
    trace3 = go.Scatter(x=debt.df_debt['date'],
                        y=debt.df_debt['total_liab_cad'],
                        mode='lines',
                        name='Total Liabilities')
    data = [trace1, trace2, trace3]
    layout = go.Layout(title='Liabilities (CAD)',
                       legend_orientation='h',
                       showlegend=True,
                       yaxis_title="CAD",
                       xaxis={
                             'rangeselector': {'buttons': [
                                 {
                                     "count": 3,
                                     "label": "3 mo",
                                     "step": "month",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 6,
                                     "label": "6 mo",
                                     "step": "month",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 1,
                                     "label": "1 yr",
                                     "step": "year",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 1,
                                     "label": "YTD",
                                     "step": "year",
                                     "stepmode": "todate"
                                 },
                                 {"step": "all"}
                             ]},
                             'rangeslider': {'visible': True},
                             'type': 'date',
                             "autorange": True
                       })
    figure = {'data': data, 'layout': layout}
    return figure


@app.callback([Output('btc_price', 'children'),
               Output('graph_ratio', 'figure')],
              [Input('interval_price', 'n_intervals')])
def interval_price_triggered(n_intervals):
    # TODO: Need to wrap this, to catch Third Party API exception
    price = update_price_label()
    figure = update_graph_ratio()
    return price, figure


def update_price_label():
    price_usd = float(tools.get_usd_price())
    curr_fx_cadusd = float(tools.get_fx_cadusd_rates(datetime.datetime.now().strftime('%Y-%m-%d'))[0])
    price_cad = int(price_usd / curr_fx_cadusd)
    return 'BTC: '+str(price_usd)+' USD / '+str(price_cad)+' CAD'


def update_graph_ratio():
    update_loans_with_current_price()
    figure = build_graph_ratio()
    return figure


def build_graph_ratio():
    data = []
    oldest_start_date = datetime.date.today()
    for loan in Loan.actives:
        if loan.start_date < oldest_start_date : oldest_start_date = loan.start_date
        trace = go.Scatter(x=loan.stats['date'],
                           y=loan.stats['collateralization_ratio'],
                           mode='lines',
                           name='$'+str(loan.current_debt_cad))
        data.append(trace)
    layout = go.Layout(title='Collateral Coverage Ratio',
                       shapes=[{'type': 'line',
                                'y0': 2, 'x0': oldest_start_date,
                                'y1': 2, 'x1': datetime.date.today(),
                                'line': {'color': 'red', 'width': 2.0, 'dash': 'dot'}}],
                       legend_orientation='h',
                       showlegend=True,
                       yaxis_title="Ratio",
                       xaxis={
                           'rangeselector': {'buttons':[
                               {
                                   "count": 3,
                                   "label": "3 mo",
                                   "step": "month",
                                   "stepmode": "backward"
                               },
                               {
                                   "count": 6,
                                   "label": "6 mo",
                                   "step": "month",
                                   "stepmode": "backward"
                               },
                               {
                                   "count": 1,
                                   "label": "1 yr",
                                   "step": "year",
                                   "stepmode": "backward"
                               },
                               {
                                   "count": 1,
                                   "label": "YTD",
                                   "step": "year",
                                   "stepmode": "todate"
                               },
                               {"step": "all"}
                           ]},
                           'rangeslider': {'visible': True},
                           'type': 'date',
                           "autorange": True
                       })
    figure = {'data': data, 'layout': layout}
    return figure


if __name__ == '__main__':
    app.run_server()
