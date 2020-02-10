#!/usr/bin/env python3

import argparse
import datetime
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
from config import set_test_mode, set_loans_input_file

import tools
from debt import Debt
from exceptions import InitializationDataNotFound, ThirdPartyApiUnavailable, InvalidLoanData
from loan import Loan, get_loans, update_loans_with_current_price, get_cost_analysis


loans = None
debt = None

parser = argparse.ArgumentParser(description='CDP stats server.')

parser.add_argument('-t', '--test', help='Specify the test suite (/tests/data/[loans-x].csv file to run')
parser.add_argument('-f', '--file', help='Specify the \'/data/[loans].csv\' file to run')

args = parser.parse_args()
if args.test:
    set_test_mode(args.test)
if args.file:
    set_loans_input_file(args.file)

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
    print('[ERROR] Invalid "loan.csv" file given. ')
    sys.exit(1)
debt = Debt()
debt.build_dataframe()


app = dash.Dash()
app.layout = html.Div([
    dcc.Interval(id='interval_price', interval=50000, n_intervals=0),
    dcc.Interval(id='interval_debt', interval=500000, n_intervals=0),

    html.H1(id='btc_price', children=''),

    html.Div([
       dcc.Graph(id='graph_cost_analysis')
    ]),


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

# Todo: Include this for user display info.
# total_coll = 0
# for l in loans:
#     total_coll += l.current_collateral
# price = 12324
# loan = 190000
# print("current collateral held by Ledn: ", total_coll)
# liquidate = (loan/price)
# print("If I wanted to liqudate (Total borrowed/\ bicoin price):", liquidate)
# print("If I want to rebalance with current price: ", liquidate * 2)
# withdraw = total_coll - (liquidate * 2)
# print(f"Could withdraw: {withdraw} - ${withdraw * price}")
# print(f"cost to rebalance (2%): {loan*(0.02)}")


@app.callback([Output('graph_debt_btc', 'figure'),
               Output('graph_debt_cad', 'figure')],
              [Input('interval_debt', 'n_intervals')])
def interval_debt_triggered(n_intervals):
    debt.update_df_with_current_price()
    figure_btc = update_graph_debt_btc()
    figure_cad = update_graph_debt_cad()
    return figure_btc, figure_cad


def update_graph_debt_btc():
    df = debt.df_debt
    trace1 = go.Scatter(x=df['date'],
                        y=df['debt_btc'],
                        mode='lines',
                        name='Debt')
    trace2 = go.Scatter(x=df['date'],
                        y=df['interest_btc'],
                        mode='lines',
                        name='Interest')
    trace3 = go.Scatter(x=df['date'],
                        y=df['total_liab_btc'],
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
                                     "count": 1,
                                     "label": "1 mo",
                                     "step": "month",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 3,
                                     "label": "3 mo",
                                     "step": "month",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 6,
                                     "label": "6 mo",
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
    df = debt.df_debt
    trace1 = go.Scatter(x=df['date'],
                        y=df['debt_cad'],
                        mode='lines',
                        name='Debt')
    trace2 = go.Scatter(x=df['date'],
                        y=df['interest_cad'],
                        mode='lines',
                        name='Interest')
    trace3 = go.Scatter(x=df['date'],
                        y=df['total_liab_cad'],
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
                                     "count": 1,
                                     "label": "1 mo",
                                     "step": "month",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 3,
                                     "label": "3 mo",
                                     "step": "month",
                                     "stepmode": "backward"
                                 },
                                 {
                                     "count": 6,
                                     "label": "6 mo",
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
               Output('graph_ratio', 'figure'),
               Output('graph_cost_analysis', 'figure')],
              [Input('interval_price', 'n_intervals')])
def interval_price_triggered(n_intervals):
    try:
        price = update_price_label()
    except ThirdPartyApiUnavailable:
        price = 'NA'
        print('[INFO] Third party API not available, could not update price.')
    finally:

        figure_ratio = update_graph_ratio()
        figure_cost_analysis = update_graph_cost_analysis()
    return price, figure_ratio, figure_cost_analysis


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
    for cdp in Loan.actives:
        if cdp.start_date < oldest_start_date : oldest_start_date = cdp.start_date
        trace = go.Scatter(x=cdp.stats['date'],
                           y=cdp.stats['coll_ratio'],
                           mode='lines',
                           name='$'+str(cdp.current_debt_cad))
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
                                   "count": 1,
                                   "label": "1 mo",
                                   "step": "month",
                                   "stepmode": "backward"
                               },
                               {
                                   "count": 3,
                                   "label": "3 mo",
                                   "step": "month",
                                   "stepmode": "backward"
                               },
                               {
                                   "count": 6,
                                   "label": "6 mo",
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
    return {'data': data, 'layout': layout}


def update_graph_cost_analysis():
    cost_data = get_cost_analysis()
    figure = build_graph_cost_analysis(cost_data)
    return figure


def build_graph_cost_analysis(cost_data):
    data = []
    red = 'rgb(255,65,54)'
    grn = 'rgb(61,153,112)'
    colors = [red if bar >= 0 else grn for bar in cost_data['diff_btc']]
    trace = go.Bar(x=cost_data['loan_id'],
                   y=cost_data['diff_btc'],
                   hovertext=cost_data['diff_percentage'],
                   name='BTC',
                   marker={'color': colors})
    data.append(trace)
    layout = go.Layout(title='Loan Cost Analysis',
                       xaxis={'type': 'category'},
                       yaxis_title='BTC')
    return {'data': data, 'layout': layout}


if __name__ == '__main__':
    app.run_server()
