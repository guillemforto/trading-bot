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
    table = table[table['PE Ratio (TTM)'] >= per_q1]
    candidates_table = table[table['PE Ratio (TTM)'] <= per_q2]

    candidates_table['% Change'] = [float(i[:-1]) for i in candidates_table['% Change']]
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


def get_5_equities_data(candidates_table):
    five_eq_symbols = []
    five_eq_data = []
    for i in range(0,5):
        (top_gainer, candidates_table) = select_top_gainer(candidates_table)
        try:
            data = get_1_equity_data(top_gainer)
        except:
            data = pd.DataFrame({})

        boolean = is_data_available(data)
        while boolean == False:
            print("No data available for ", top_gainer, ". We need to wait for 1min...", sep="")
            time.sleep(60)
            (top_gainer, candidates_table) = select_top_gainer(candidates_table)
            data = get_1_equity_data(top_gainer)
            boolean = is_data_available(data)
        five_eq_symbols.append(top_gainer)
        five_eq_data.append(data)

    print("Done!")
    return((five_eq_symbols, five_eq_data))
