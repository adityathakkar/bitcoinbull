from flask import Flask, render_template, request
import requests
import datetime as dt 
import os 
import json 
import pandas as pd
import numpy as np


###############################################################
# Global Variables
###############################################################
api_token = "D74EY3H0MX9X5K33"


###############################################################
###############################################################
# Helper Functions
###############################################################
###############################################################

# Get BTC prices from alpha vantage
def get_crypto_prices(symbol):
    r = requests.get("https://www.alphavantage.co/query?function=DIGITAL_CURRENCY_DAILY&symbol="+symbol+"&outputsize=full&market=USD&apikey="+api_token)
    crypto_ts = json.loads(r.text)
    prices = crypto_ts['Time Series (Digital Currency Daily)']
    crypto_df = pd.read_json(json.dumps(prices), orient="index")
    return crypto_df

# Get S&P 500 prices from alpha vantage
def get_equity_prices(symbol):
    r = requests.get("https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol="+symbol+"&outputsize=full&apikey="+api_token)
    ts = json.loads(r.text)
    prices = ts["Time Series (Daily)"]
    df = pd.read_json(json.dumps(prices), orient="index")
    return df

# Get pricing data on server start
# This way, all pricing data is cached and we dont have to ring the pricing APIs, which are slow and 
# Cause a massive user bottleneck
def initiate():
	app = Flask(__name__)
	btc_df = get_crypto_prices('BTC')
	# Get S&P 500 Index Prices
	sp500_df = get_equity_prices('^GSPC')
	sp500_df.truncate('2014-04-01')
	combined_df = btc_df.join(sp500_df)
	combined_df = combined_df.dropna()
	pricing_df = combined_df[['5. adjusted close', '4b. close (USD)']]
	# Rename some columns
	pricing_df = pricing_df.rename(columns={'5. adjusted close': 'S&P 500 Index', "4b. close (USD)": "BTC"})
	pricing_df['Date'] = pricing_df.index
	pricing_df = pricing_df[['Date','S&P 500 Index', 'BTC']]
	del combined_df
	return [app, pricing_df]


# Take in amount of cash, buy shares at start date and 
# Return what the portfolio metrics would be at the end date
# Output: [returns, alpha, beta, sharpe ratio]
def get_portfolio_value(start_date, end_date, cash, sp_weight, btc_weight, pricing_df):
    strt = dt.datetime.strptime(start_date,"%Y-%m-%d")
    end = dt.datetime.strptime(end_date,"%Y-%m-%d")
    pricing_df = pricing_df[pricing_df['Date'] >= strt]
    pricing_df = pricing_df[pricing_df['Date'] <= end]

    btc_shares = (cash*btc_weight)/pricing_df['BTC'][0]
    sp_shares = (cash*sp_weight)/pricing_df['S&P 500 Index'][0]
    
    port_df = pd.DataFrame(index=pricing_df.index)
    port_df['Value'] = sp_shares*pricing_df['S&P 500 Index'] + btc_shares*pricing_df['BTC']

    # Calculate beta
    
    port_cov = port_df['Value'].cov(pricing_df['S&P 500 Index']*(cash/pricing_df['S&P 500 Index'][0]))
    mkt_var = (pricing_df['S&P 500 Index']*((cash/pricing_df['S&P 500 Index'][0]))).var()
    
    beta = port_cov/mkt_var
        
    # Calculate alpha
    
    port_return = port_df['Value'][-1]/port_df['Value'][0]
    mkt_return = (pricing_df['S&P 500 Index'][-1]/pricing_df['S&P 500 Index'][0])
    alpha = port_return-beta*mkt_return 
    
    # Calculate Sharpe ratio
    port_df['Daily Returns'] = port_df['Value'].pct_change(1)
    sharpe = port_df['Daily Returns'].mean()/port_df['Daily Returns'].std()*(252**0.5)
    port_df['Returns'] = port_df['Value']/cash
    
    return [port_return, alpha, beta, sharpe, port_df]



app,pricing_df = initiate()

@app.route('/')
def home():
	yesterday = dt.date.today() - dt.timedelta(days=1)
	ystrday = yesterday.strftime('%Y-%m-%d')
	get_portfolio_value('2014-04-05', ystrday, 1000000, 0.99, 0.01, pricing_df)
	return render_template('home.html')



@app.route('/getChartVals')
def get_chart_vals():
	start_date = request.args.get('start')
	end_date =  request.args.get('end')
	btc_weight =  float(request.args.get('btc_weight'))
	sp_weight =  float(request.args.get('sp_weight'))
	[port_return, alpha, beta, sharpe, port_df] = get_portfolio_value(start_date, end_date, 1000000, sp_weight, btc_weight, pricing_df)
	port_df['Returns'] = port_df["Returns"]-1
	port_df['Date'] = port_df.index
	port_df['Date'].apply(lambda x: str(x.strftime('%Y-%m-%d')))
	resp = {}
	resp["Returns"] =port_df['Returns'].to_json(orient='values')
	resp["Dates"] =port_df['Date'].to_json(orient='values')
	resp["Alpha"] = alpha 
	resp["Beta"] = beta
	resp["Sharpe"] = sharpe
	return resp
  


