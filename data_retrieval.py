########################################################
############### DATA RETRIEVAL FUNCTIONS ###############
########################################################

### IMPORTATION ###
import numpy as np
import pandas as pd

import requests

from datetime import datetime
from datetime import timedelta
import time
import pytz

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

import supres as supres


### GLOBAL ENV ###
    # time
timezone = pytz.timezone("America/New_York")

    # alphavantage api
apikey = '0FA4MXDSORI7KI96'
ts = TimeSeries(key=apikey, output_format='pandas')
ti = TechIndicators(key=apikey)


### FUNCTIONS ###
def get_candidate_equities(url):
    table = pd.read_html(requests.get(url).content)[0]

    # Low PER: Q1 < PE ratio (TTM) < Q2
    table = table[~table['PE Ratio (TTM)'].isna()]
    per_q1 = table['PE Ratio (TTM)'].quantile(0.25)
    per_q2 = table['PE Ratio (TTM)'].quantile(0.5)
    q1q2 = table[table['PE Ratio (TTM)'] >= per_q1]
    q1q2 = q1q2[q1q2['PE Ratio (TTM)'] <= per_q2]

    if len(q1q2) > 10:
        candidates_table = q1q2
    else:
        candidates_table = table

    tmp = candidates_table['% Change'].apply(lambda x: float(x[:-1])).values
    candidates_table = candidates_table.drop(['% Change'], axis = 1)
    candidates_table['% Change'] = tmp

    candidates_table.sort_values(by="% Change", ascending=False, inplace=True)
    candidates_table.reset_index(inplace=True, drop=True)

    return(candidates_table)


def select_top_gainer(candidates_table):
    top_gainer = candidates_table['Symbol'][0]
    candidates_table.drop(index=0, inplace=True)
    candidates_table.reset_index(inplace=True, drop=True)
    return((top_gainer, candidates_table))


def get_1_equity_data(symbol):
    print("Trying to get data for ", symbol, sep="")
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min', outputsize='full')
    data.sort_index(inplace=True)
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    data = data[data.index.day == ny_now.day] # subset to intraday prices
    return(data)


def is_data_available(data):
    boolean = True
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    if data.empty:
        boolean = False
    else:
        set_of_days = list(data[~data.index.day.duplicated()].index.day)
        if (ny_now.day not in set_of_days):
            boolean = False
    return(boolean)


def are_supres_appropriate(five_eq_symbols):
    final_five_eq_symbols = []

    for ticker in five_eq_symbols:
        h = supres.get_hist_data(ticker)
        try:
            (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(h, window=len(h), errpct=0.01, sortError=False, accuracy=1)
            (best_sup, best_res) = supres.filter_best_supres(mintrend, maxtrend, h)
            supres.plot_supres(h, minimaIdxs, maximaIdxs, best_sup, best_res)
            print("Write yes if it's it okay to keep", ticker)
            x = input()
            if x == 'yes':
                final_five_eq_symbols.append(ticker)
        except:
            print("No suitable support nor resistance found")
            pass

    return(final_five_eq_symbols)


def get_5_equities_data(candidates_table):
    five_eq_symbols = []
    five_eq_data = []
    while len(five_eq_symbols) < 5:
        (top_gainer, candidates_table) = select_top_gainer(candidates_table)
        try:
            data = get_1_equity_data(top_gainer)
        except:
            data = pd.DataFrame({})

        boolean = is_data_available(data)
        while boolean == False:
            print("No data available for ", top_gainer, ". We need to wait for 1min...", sep="")
            time.sleep(50)
            (top_gainer, candidates_table) = select_top_gainer(candidates_table)
            data = get_1_equity_data(top_gainer)
            boolean = is_data_available(data)

        five_eq_symbols.append(top_gainer)
        five_eq_data.append(data)

    final_five_eq_symbols = are_supres_appropriate(five_eq_symbols)

    print("Done!")
    return((final_five_eq_symbols, five_eq_data))


def update_5_equities_data(five_eq_symbols):
    five_eq_data = []
    for symbol in five_eq_symbols:
        five_eq_data.append(get_1_equity_data(symbol))
    print("Done!")
    return(five_eq_data)


url = 'https://finance.yahoo.com/gainers'
candidates_table = get_candidate_equities(url)
(five_eq_symbols, five_eq_data) = get_5_equities_data(candidates_table)
