
# IMPORTATION #
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

import numpy as np
import pandas as pd
import math
from scipy.signal import argrelextrema

from datetime import datetime
from datetime import timedelta
import calendar
import time
import pytz
import holidays

import requests

from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

timezone = pytz.timezone("America/New_York")



# Your key here
key = '0FA4MXDSORI7KI96'
# Chose your output format, or default to JSON (python dict)
ts = TimeSeries(key, output_format='pandas')
ti = TechIndicators(key)

def subselect_intraday(data):
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    subset = data[data.index.day == ny_now.day]
    return(subset)


# Visualization
def simple_plot(data):
    figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
    data['4. close'].plot()
    plt.tight_layout()
    plt.grid()
    plt.show()


# Get the data, returns a tuple
data, meta_data = ts.get_intraday(symbol='MSFT', interval='1min', outputsize='full')
data.sort_index(inplace=True)
data = subselect_intraday(data)

simple_plot(data)

data.index.day == 27


def detect_trend(prices_df):
    if prices_df['4. close'][0] < prices_df['4. close'][len(prices_df)-1]:
        return("upward")
    elif prices_df['4. close'][0] < prices_df['4. close'][len(prices_df)-1]:
        return("downward")

detect_trend(prices_df)


# Finding minima and maxima
def get_minmax(prices_df, smoothing = 3, window_range = 8):
    # smooth to find local min max
    smooth_prices = prices_df['4. close'].rolling(window=smoothing).mean().dropna()
    simple_plot(pd.DataFrame(smooth_prices))
    local_max = argrelextrema(smooth_prices.values, np.greater)[0]
    local_min = argrelextrema(smooth_prices.values, np.less)[0]

    price_local_max_dt = []
    for i in local_max:
        if (i > window_range) and (i < len(prices_df) - window_range):
            price_local_max_dt.append(
                prices_df.iloc[i-window_range:i+window_range]['4. close'].idxmax()
                )

    price_local_min_dt = []
    for i in local_min:
        if (i > window_range) and (i < len(prices_df) - window_range):
            price_local_min_dt.append(
                prices_df.iloc[i-window_range:i+window_range]['4. close'].idxmin()
                )

    maxima = pd.DataFrame(prices_df.loc[price_local_max_dt])
    minima = pd.DataFrame(prices_df.loc[price_local_min_dt])
    max_min = pd.concat([maxima, minima]).sort_index()
    max_min = max_min[~max_min.index.duplicated()]

    # plot
    figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
    prices_df['4. close'].plot()
    plt.scatter(max_min.index, max_min.values, color='orange', alpha=.5)
    plt.tight_layout()
    plt.grid()
    plt.show()

    return(max_min)

prices_df = pd.DataFrame(data['4. close'])
prices_df.reset_index(inplace=True, drop=True)
minmax = get_minmax(prices_df, smoothing = 3, window_range = 2)



# Finding patterns
from collections import defaultdict

def find_patterns(minmax):
    patterns = defaultdict(list)

    # Window range is 5 units
    for i in range(5, len(minmax)):
        window = minmax.iloc[i-5:i]

        # Pattern must play out in less than n units
        # If condition is filled, pattern recog below won't be executed
        n = 100
        if window.index[-1] - window.index[0] > n:
            continue

        print("HEYY")
        print(window)

        a, b, c, d, e = [i for i in window.iloc[0:5]['4. close']]

        # IHS
        if a<b and c<a and c<e and c<d and e<d and abs(b-d) <= np.mean([b,d])*0.02:
            patterns['IHS'].append((window.index[0], window.index[-1]))

    return(patterns)

patterns = find_patterns(minmax)
patterns
