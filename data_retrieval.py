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
import trendln

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
    top_gainer_name = candidates_table['Name'][0]
    candidates_table.drop(index=0, inplace=True)
    candidates_table.reset_index(inplace=True, drop=True)
    return((top_gainer, top_gainer_name, candidates_table))


def get_1_equity_data(symbol, symbol_name=''):
    if symbol_name == '':
        print("Updating data for ", symbol, sep="")
    else:
        print("Trying to get data for ", symbol, ' - ', symbol_name, sep="")

    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min', outputsize='full')
    data.sort_index(inplace=True)
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    # data = data[data.index.day == 8] # subset to intraday prices
    data = data[data.index.day == ny_now.day] # subset to intraday prices
    return(data)


def is_data_available(data):
    boolean = True
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    if data.empty:
        boolean = False
    else:
        set_of_days = list(data[~data.index.day.duplicated()].index.day)
        if (ny_now.day not in set_of_days): # (8 not in set_of_days)
            boolean = False
    return(boolean)


def is_supres_appropriate(symbol):
    boolean = False
    h = supres.get_hist_data(symbol)
    (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(h, window=len(h), errpct=0.01, sortError=False, accuracy=1)
    try:
        (best_sup, best_res) = supres.filter_best_supres(mintrend, maxtrend, h)
        supres.plot_supres(h, minimaIdxs, maximaIdxs, best_sup, best_res)
        print("Is it okay to keep", symbol, '?')
        x = input("[y/n]: ")
        # x = 'y'
        if x == 'y' or x == 'Y':
            boolean = True
    except:
        print("No suitable support / resistance found for", symbol, '\n')

    return(boolean)


def get_supres(symbol):
    h = supres.get_hist_data(symbol)
    (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(h, window=len(h), errpct=0.01, sortError=False, accuracy=1)
    (best_sup, best_res) = supres.filter_best_supres(mintrend, maxtrend, h)
    # sup_slope, sup_intercept, res_slope, res_intercept
    return((best_sup[1][0], best_sup[1][1], best_res[1][0], best_res[1][1]))



def get_5_equities_data(candidates_table):
    five_eq_symbols = []
    five_eq_data = []
    while len(five_eq_symbols) < 5:

        (top_gainer, top_gainer_name, candidates_table) = select_top_gainer(candidates_table)
        try:
            data = get_1_equity_data(top_gainer, top_gainer_name)
        except:
            data = pd.DataFrame({})


        boolean = is_data_available(data)
        if boolean == False:
            print("No intraday data available for ", top_gainer, ". Please wait a minute...", sep="")
            boolean2 = False
        else:
            print("Intraday data is available for", top_gainer)
            boolean2 = is_supres_appropriate(top_gainer)

        while boolean == False or boolean2 == False:
            time.sleep(30)
            (top_gainer, top_gainer_name, candidates_table) = select_top_gainer(candidates_table)
            data = get_1_equity_data(top_gainer, top_gainer_name)
            boolean = is_data_available(data)
            if boolean == False:
                print("No intraday data available for ", top_gainer, ". Please wait a minute...", sep="")
                boolean2 = False
            else:
                print("Intraday data is available for", top_gainer)
                boolean2 = is_supres_appropriate(top_gainer)

            if len(candidates_table) == 0:
                print('\nNo stocks left in the candidates table.')
                break

        five_eq_symbols.append(top_gainer)
        five_eq_data.append(data)
        print('\nTicker added to the list:', five_eq_symbols, '\n')

        if len(candidates_table) == 0:
            print('\nNo stocks left in the candidates table.')
            break

    # Getting support and resistances
    five_eq_supres = []
    for symbol in five_eq_symbols:
        five_eq_supres.append(get_supres(symbol))

    print('The final list is:', five_eq_symbols, '\n')

    print('Done!')
    return((five_eq_symbols, five_eq_data, five_eq_supres))



def update_5_equities_data(five_eq_symbols):
    print("\nUpdating data for our equities:")
    five_eq_data = []
    for symbol in five_eq_symbols:
        five_eq_data.append(get_1_equity_data(symbol))
    print("Done!\n")
    return(five_eq_data)
