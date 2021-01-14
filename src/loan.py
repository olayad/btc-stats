#!/usr/bin/env/ python3

import pandas as pd
import datetime
import itertools

import config as cfg
import tools
from exceptions import InitializationDataNotFound, InvalidData
from price_data import PriceData

df_btcusd = PriceData().df_btcusd


class Loan:
    counter = 1
    actives = []
    closed = []
    input_file_df = None

    def __init__(self, start_date, wallet_address, admin_fee):
        self.stats = pd.DataFrame()
        self.collateral_history = {}    # {date:{'type': _ , 'amount': _}
        self.debt_history_cad = {}      # {date: amount}
        self.current_collateral = 0
        self.current_debt_cad = 0
        self.start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        self.wallet_address = wallet_address
        self.admin_fee = admin_fee
        self.closed_date = ""
        self.id = self.counter
        Loan.counter += 1

    # TODO: Rename below 'calculate_stats'
    def populate_stats(self):
        loan_start_date = pd.Timestamp(self.start_date)
        self.stats['date'] = df_btcusd[df_btcusd['Date'] >= loan_start_date]['Date']
        self.stats['btc_price_usd'] = df_btcusd[df_btcusd['Date'] >= loan_start_date]['Last']
        end_date = self.stats['date'].iloc[0].strftime("%Y-%m-%d")
        self.stats['fx_cadusd'] = tools.get_historic_fx_cadusd_rates(self.stats['date'], str(self.start_date), str(end_date))
        self.stats['btc_price_cad'] = [round(row['btc_price_usd'] / float(row['fx_cadusd']), 1) for _, row in self.stats.iterrows()]
        self.stats['debt_cad'] = self.populate_debt_cad()
        self.stats['coll_amount'] = self.populate_collateral_amounts()
        self.stats['interest_cad'] = self.calculate_interest()
        self.stats['ltv'] = self.calculate_loan_ltv()

    def populate_debt_cad(self):
        borrowed_cad_df = []
        dates_which_had_borrowed_cad_update = list(self.debt_history_cad.keys())
        curr_borrowed = self.current_debt_cad
        for index, row in self.stats.iterrows():
            borrowed_cad_df.append(curr_borrowed)
            if row['date'] in dates_which_had_borrowed_cad_update:
                curr_borrowed -= self.debt_history_cad[row['date']]
                dates_which_had_borrowed_cad_update.pop()
        return borrowed_cad_df

    def populate_collateral_amounts(self):
        collateral_df = []
        dates_which_had_collateral_update = list(self.collateral_history.keys())
        curr_collateral = self.current_collateral
        for index, row in self.stats.iterrows():
            collateral_df.append(curr_collateral)
            if row['date'] in dates_which_had_collateral_update:
                if self.collateral_history[row['date']]['type'] is cfg.COLLATERAL_INCREASED:
                    curr_collateral -= self.collateral_history[row['date']]['amount']
                else:
                    curr_collateral += self.collateral_history[row['date']]['amount']
                dates_which_had_collateral_update.pop()
        return collateral_df

    def calculate_interest(self):
        df_interest = []
        interest = 0
        for _, row in self.stats[::-1].iterrows():
            daily_interest = cfg.DAILY_INTEREST * row['debt_cad']
            interest += daily_interest
            df_interest.insert(0, round(interest, 2))
        return df_interest

    def calculate_loan_ltv(self):
        ltv_values = []
        for _, row in self.stats.iterrows():
            ltv = calculate_ltv(row['debt_cad'], row['interest_cad'], row['coll_amount'], row['btc_price_cad'])
            ltv_values.append(ltv)
        return ltv_values

    def update_stats_with_current_price(self, date_to_update, btc_price_usd):
        if self.date_to_update_is_not_in_stats(date_to_update):
            self.append_new_row_to_stats(date_to_update, btc_price_usd)
        else:
            self.update_row_prices(date_to_update, btc_price_usd)
            self.update_row_ltv(date_to_update)

    def date_to_update_is_not_in_stats(self, date_to_update):
        df_earliest_date = self.stats.iloc[0]['date']
        return df_earliest_date != date_to_update

    def append_new_row_to_stats(self, date_to_update, btc_price_usd):
        fx_rate = float(tools.get_curr_fx_cadusd_rate())
        btc_price_cad = round(btc_price_usd / fx_rate, 1)
        interest_cad = self.calculate_new_row_interest()
        ltv = calculate_ltv(self.current_debt_cad, interest_cad, self.current_collateral, btc_price_cad)
        new_row = pd.DataFrame({'date': [date_to_update],
                                'btc_price_usd': [btc_price_usd],
                                'fx_cadusd': [fx_rate],
                                'btc_price_cad': [btc_price_cad],
                                'debt_cad': [self.current_debt_cad],
                                'coll_amount': [self.current_collateral],
                                'ltv': [ltv],
                                'interest_cad': [interest_cad]})
        self.stats = pd.concat([new_row, self.stats], sort=True).reset_index(drop=True)

    def update_row_prices(self, date_to_update, btc_price_usd):
        fx_rate = float(tools.get_curr_fx_cadusd_rate())
        btc_price_cad = round(btc_price_usd / fx_rate, 1)
        self.stats.loc[self.stats['date'] == date_to_update, 'fx_cadusd'] = fx_rate
        self.stats.loc[self.stats['date'] == date_to_update, 'btc_price_usd'] = btc_price_usd
        self.stats.loc[self.stats['date'] == date_to_update, 'btc_price_cad'] = btc_price_cad

    def update_row_ltv(self, date_to_update):
        btc_price_cad = self.stats.loc[self.stats['date'] == date_to_update, 'btc_price_cad']
        coll_amount = self.stats.loc[self.stats['date'] == date_to_update, 'coll_amount']
        debt_cad = self.stats.loc[self.stats['date'] == date_to_update, 'debt_cad']
        interest_cad = self.stats.loc[self.stats['date'] == date_to_update, 'interest_cad']
        new_ltv = calculate_ltv(debt_cad, interest_cad, coll_amount, btc_price_cad)
        self.stats.loc[self.stats['date'] == date_to_update, 'ltv'] = new_ltv

    def calculate_new_row_interest(self):
        interest_accumulated = self.stats.iloc[0]['interest_cad']
        return round(interest_accumulated + (cfg.DAILY_INTEREST * self.current_debt_cad), 2)

    def __str__(self):
        return (f'ID:{self.id:0>2d}, current_debt:${self.current_debt_cad:6d}, '
                f'current_collateral:{self.current_collateral}, admin_fee:{self.admin_fee}, '
                f'start_date:{self.start_date}, closed_date:{self.closed_date}')


def get_loans():
    if len(Loan.actives) == 0: init_loans()
    return Loan.actives


def init_loans():
    Loan.input_file_df = load_input_file()
    Loan.actives = create_loan_instances()
    for loan in Loan.actives: loan.populate_stats()
    Loan.closed = archive_closed_loans(Loan.actives)


def load_input_file():
    file = ''
    try:
        file = './data/'+cfg.TEST_MODE if cfg.TEST_MODE else cfg.LOANS_INPUT_FILE
        print('[INFO] Initializing loans with file: '+file)
        df = pd.read_csv(file)
    except FileNotFoundError:
        print('[ERROR] Could not find file [{}]'.format(file))
        raise InitializationDataNotFound
    df.set_index('num', inplace=True)
    return df


def create_loan_instances():
    active_loans = []
    for index, row in Loan.input_file_df.iterrows():
        if row['type'] is cfg.NEW_LOAN:
            if new_loan_entry_is_valid(active_loans, row):
                active_loans.append(instantiate_new_loan(row))
                update_collateral_records(active_loans, row)
                update_debt_cad_records(active_loans, row)
        if row['type'] is cfg.COLLATERAL_INCREASED or row['type'] is cfg.COLLATERAL_DECREASED:
            update_collateral_records(active_loans, row)
        if row['type'] is cfg.DEBT_CAD_INCREASED:
            update_debt_cad_records(active_loans, row)
        if row['type'] is cfg.CLOSED_LOAN:
            update_closed_loan_date(active_loans, row)
    return active_loans


def new_loan_entry_is_valid(active_loans, csv_entry):
    for cdp in active_loans:
        if csv_entry['wallet_address'] == cdp.wallet_address:
            raise InvalidData('Trying to create a loan that already '
                                  'exists:{}'.format(cdp.wallet_address))
    return True


def instantiate_new_loan(entry):
    return Loan(entry['start_date'], entry['wallet_address'], entry['admin_fee'])


def update_collateral_records(loans, csv_entry):
    for cdp in loans:
        if cdp.wallet_address == csv_entry['wallet_address']:
            new_entry = {pd.Timestamp(csv_entry['date_update']): {'type': csv_entry['type'],
                                                                  'amount': csv_entry['coll_amount']}}
            cdp.collateral_history.update(new_entry)
            if csv_entry['type'] is cfg.COLLATERAL_DECREASED:
                cdp.current_collateral -= csv_entry['coll_amount']
            else:
                cdp.current_collateral += csv_entry['coll_amount']


def update_debt_cad_records(loans, csv_entry):
    for cdp in loans:
        if cdp.wallet_address == csv_entry['wallet_address']:
            cdp.debt_history_cad.update({pd.Timestamp(csv_entry['date_update']): csv_entry['debt_cad']})
            cdp.current_debt_cad += csv_entry['debt_cad']


def update_loans_with_current_price(date_given: object = 0, price_given: object = 0) -> object:
    date = tools.get_current_date_for_exchange_api() if not date_given else date_given
    price = price_given if price_given else tools.get_usd_price()
    for cdp in Loan.actives: cdp.update_stats_with_current_price(pd.Timestamp(date), float(price))


def find_oldest_active_loan_date():
    oldest_active = datetime.datetime.today().date()
    for cdp in Loan.actives:
        if cdp.start_date < oldest_active: oldest_active = cdp.start_date
    return oldest_active


def get_loans_generating_interest_at_date(date):
    loans_active_at_date = []
    for cdp in itertools.chain(Loan.actives, Loan.closed):
        if cdp.start_date <= date:
            if cdp.closed_date and cdp.closed_date <= date:
                continue
            else:
                loans_active_at_date.append(cdp)
    return loans_active_at_date


def get_btc_cad_price_data_from_oldest_loan():
    btc_cad_price = []
    oldest_active = find_oldest_active_loan_date()
    for cdp in Loan.actives:
        if cdp.start_date == oldest_active: btc_cad_price = cdp.stats['btc_price_cad']
    return btc_cad_price


def get_cost_analysis():
    diff_percentage, diff_btc, loan_id = [], [], []
    for cdp in Loan.actives:
        start_total_debt = round(cdp.stats.iloc[-1]['debt_cad'] +
                                 cdp.stats.iloc[-1]['interest_cad'] +
                                 cdp.admin_fee, 4)
        start_cost_btc = round(start_total_debt / cdp.stats.iloc[-1]['btc_price_cad'], 4)
        end_total_debt = round(cdp.stats.iloc[0]['debt_cad'] + cdp.stats.iloc[0]['interest_cad'] + cdp.admin_fee, 4)
        end_cost_btc = round(end_total_debt / cdp.stats.iloc[0]['btc_price_cad'], 4)
        loan_id.append(str(cdp.id)+'- $'+str(cdp.current_debt_cad))
        diff_btc.append(round(end_cost_btc - start_cost_btc, 4))
        percent_change = round((((end_cost_btc * 100) / start_cost_btc) - 100), 2)
        diff_percentage.append("Start cost: "+str(start_cost_btc) +
                               " btc<br>Current cost: "+str(end_cost_btc) +
                               " btc<br>Change: " + str(percent_change) + "%")
    loan_id.append("Total")
    diff_btc.append(round(sum(diff_btc), 4))
    return {"loan_id": loan_id, "diff_btc": diff_btc, "diff_percentage": diff_percentage}


def update_closed_loan_date(actives, csv_entry):
    for cdp in actives:
        if cdp.wallet_address == csv_entry['wallet_address']:
            cdp.closed_date = datetime.datetime.strptime(csv_entry['date_update'], '%Y-%m-%d').date()


def archive_closed_loans(active_loans):
    closed_loans, to_remove = [], []
    for i, cdp in enumerate(active_loans):
        if cdp.closed_date:
            closed_loans.append(cdp)
            to_remove.append(i)
    [active_loans.pop(i) for i in sorted(to_remove, reverse=True)]
    return closed_loans


def get_closed_loan_dates():
    return [cdp.closed_date for cdp in Loan.closed]


def calculate_ltv(debt_cad, interest_cad, coll_amount, btc_price_cad):
    return round((debt_cad + interest_cad) / (coll_amount * btc_price_cad), 2)
    # TODO: change ltv to percentage in app.py LTV graph
    # return round(((debt_cad + interest_cad) / (coll_amount * btc_price_cad) * 100), 2)

