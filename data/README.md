# /cdp-stats/data/

This folder contains files required for running the tool in Production:

- btcusd.csv: File is generated in automatic when app.py is executed. It uses information from Bitcoin
exchange API.
- loans.csv: File contains information related to the active loans and it has the format of:

num,type,wallet_address,collateral_amount,start_date,debt_cad,date_update

# Todo: create a table that explains each column

