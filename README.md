# CDP Stats Tool

This tool generates stats on Collaterized Debt Positions (CDP) using Bitcoin (BTC) as collateral.
The tool will obtain historic BTCUSD data information from Quandl and Bitfinex to calculate 
a Collateralization Ratio and use Bank Of Canada data (CADUSD exchange rate)
to calculate BTC prices in CAD. 

![cdp-stats-ui](static/ui.png)

## Prerequisites

+ Clone this repository and install `requirements.txt`.

+ This program uses two files for loan and savings inputs.
  + Loan sample file provided at (`/cdp-stats/data/loan-sample.csv`). 
  #TODO: Create sample file
  + Savings sample file provided at (`/cdp-stats/data/savings-sample.csv`). 
  

### Loan file

To use your own data, create `/cdp-stats/data/loans.csv`, a file that will contain the following information for every movement in each CDP.

```
num,type,wallet_address,coll_amount,start_date,debt_cad,date_update,admin_fee
 ```

| CSV column   |Description|
| ---------|-----------|
| num      |(int) Consecutive counter used as index | 
| type     |(int) type of CDP movement,|
| |`0` new new loan|
| |`1` collateral increase|
| |`2` collateral decrease| 
| |`3` debt (borrowed CAD) increased|
| |`4` closed loan|
|wallet_address|(str) Bitcoin address used to deposit collateral|
|coll_amount|(float) Amount of BTC increased/decreased by `type` movement|
|start_date|(YYYY-MM-DD) Date loan became active|
|debt_cad|(float) Amount of CAD increased by `type` movement|
|date_update|(YYYY-MM-DD) Date loan reflected `type` movement|
|admin_fee|(int) Fee charged at the start of loan|

### Savings file

To use your own data, create `/cdp-stats/data/savings.csv`.

```
num,type,saving_amount_btc,start_date,interest_rate
 ```

| CSV column   |Description|
| ---------|-----------|
| num      |(int) Consecutive counter used as index | 
| type     |(int) type of movement,|
| |`0` amount of BTC savings increased|
| |`1` amount of BTC savings decreased|
| |`2` interest rate change|

## Running the application

To run the application (by default, uses for `/data/loans.csv` file),  

```
$ cd [HOME]/cdp-stats/src/
$ ./app.py
```

To run the application using a different input file data, run the application with `--f [input_file.csv]`.

To use the sample file provided, 

```
$ ./app.py --f ../data/loans-sample.csv
```

Open `http://127.0.0.1:8050/` in your web browser.

## Running the tests

To run the entire test suite,

```
$ cd [HOME]/cdp-stats/tests
$ ./runner.py all
```

To test specific modules,

```
$ ./runner.py loan
$ ./runner.py debt
$ ./runner.py tools
```

## Author

Daniel Olaya
