import pandas as pd
from loan import Loan, find_oldest_active_loan_date, get_loans_generating_interest_at_date, \
    get_btc_cad_price_data_from_oldest_loan
import datetime


class Debt:
    def __init__(self):
        self.df_debt = pd.DataFrame()

    def build_dataframe(self):
        btc_cad_price = []
        interest_cad = []
        debt = []
        dates = []
        oldest_active_loan_date = pd.to_datetime(find_oldest_active_loan_date())
        most_recent_day_in_stats = Loan.actives[0].stats.iloc[0]['date']
        curr_date = most_recent_day_in_stats
        loans_generating_interest_at_date = get_loans_generating_interest_at_date(curr_date)
        while curr_date != (oldest_active_loan_date - datetime.timedelta(days=1)):
            borrowed_sum = interest_sum = 0
            for cdp in loans_generating_interest_at_date:
                borrowed_sum += cdp.stats[cdp.stats['date'] == curr_date]['debt_cad'].values[0]
                interest_sum += cdp.stats[cdp.stats['date'] == curr_date]['interest_cad'].values[0]
            dates.append(curr_date)
            interest_cad.append(round(interest_sum, 2))
            debt.append(round(borrowed_sum, 2))
            curr_date -= datetime.timedelta(days=1)
            loans_generating_interest_at_date = get_loans_generating_interest_at_date(curr_date)
        self.df_debt = pd.DataFrame({'date': dates,
                                'btc_price_cad': get_btc_cad_price_data_from_oldest_loan(),
                                'debt_cad': debt,
                                'interest_cad': interest_cad})
        self.df_debt['total_liab_cad'] = self.calculate_total_liabilities_cad()
        self.df_debt['interest_btc'] = self.calculate_interest_in_btc()
        self.df_debt['debt_btc'] = self.calculate_debt_in_btc()
        self.df_debt['total_liab_btc'] = self.calculate_total_liabilities_btc()
        return self.df_debt
        # print(self.df_debt)

    def calculate_total_liabilities_cad(self):
        liabilities_cad = []
        for _, row in self.df_debt.iterrows():
            liabilities_cad.append(round((row['debt_cad'] + row['interest_cad']), 4))
        return liabilities_cad

    def calculate_interest_in_btc(self):
        interest_btc = []
        for _, row in self.df_debt.iterrows():
            interest_btc.append(round((row['interest_cad'] / row['btc_price_cad']), 4))
        return interest_btc

    def calculate_debt_in_btc(self):
        debt_btc = []
        for _, row in self.df_debt.iterrows():
            debt_btc.append(round((row['debt_cad'] / row['btc_price_cad']), 4))
            # print('debt_cad:{}, btc_price:{}, debt_btc:{}'.format(row['debt_cad'], row['btc_price_cad'], (row['debt_cad'] / row['btc_price_cad'])))
        return debt_btc

    def calculate_total_liabilities_btc(self):
        liabilities_btc = []
        for _, row in self.df_debt.iterrows():
            liabilities_btc.append(round((row['debt_btc'] + row['interest_btc']), 4))
        return liabilities_btc

    def update_debt_df_with_current_price(self):
        self.df_debt['btc_price_cad'] = get_btc_cad_price_data_from_oldest_loan()
        self.df_debt['debt_btc'] = self.calculate_debt_in_btc()
        self.df_debt['interest_btc'] = self.calculate_interest_in_btc()
        self.df_debt['total_liab_btc'] = self.calculate_total_liabilities_btc()
        # print(Loan.actives[0].stats.head())
        # print('new_debt after price update\n', Loan.df_debt.head())
        # print()
        # print()




