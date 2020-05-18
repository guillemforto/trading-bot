########################################################
################## PATTERN DETECTION ###################
########################################################

### IMPORTATION ###
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

from datetime import datetime
from datetime import timedelta
import pytz

import numpy as np
import pandas as pd
import math
from scipy.signal import argrelextrema

import fbprophet

from matplotlib.pyplot import figure
import matplotlib.pyplot as plt


### FUNCTIONS ###
def subselect_intraday(data):
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(globalenv.timezone)
    subset = data[data.index.day == ny_now.day]
    return(subset)


# Visualization
def simple_plot(data):
    figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
    data['y'].plot()
    plt.tight_layout()
    plt.grid()
    plt.show()


# Get the data, returns a tuple
prices, meta_data = globalenv.ts.get_intraday(symbol='ZM', interval='1min', outputsize='full')

#prices.sort_index(inplace=True)
prices = prices[prices.index.day == 1]
prices = prices[prices.index.hour >= 14]
prices = prices[prices.index.hour < 15]
#prices.reset_index(inplace=True, drop=False)

prices = prices[['4. close']]
prices = prices.rename(columns={'date': 'ds', '4. close': 'y'})

simple_plot(prices)


# Bolinger bands
data, meta_data = globalenv.ti.get_bbands(symbol='ZM', interval='1min', time_period=20)
data = data[data.index.day == 1]
data = data[data.index.hour >= 14]
data = data[data.index.hour < 15]

figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
prices['y'].plot()
data.plot()
plt.tight_layout()
plt.grid()
plt.show()

# def detect_overbought_market()


# SMA
data, meta_data = globalenv.ti.get_sma(symbol='ZM', interval='1min', time_period=200, series_type='close')
data = data[data.index.day == 1]
data = data[data.index.hour >= 14]
data = data[data.index.hour < 15]

figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
plt.plot(data)
plt.plot(prices)
plt.tight_layout()
plt.grid()
plt.show()


def detect_trend(prices, sma_data):
    """ direction = 0 => no clear trend
        direction = 1 => downward trend
        direction = 2 => upward trend """
    direction = 0
    result = pd.merge(prices, sma_data, on='date')
    prop_up = round(sum(result.y > result.SMA) / len(result) * 100, 2)
    prop_down = round(sum(result.SMA > result.y) / len(result) * 100, 2)
    if prop_up > 80:
        direction = 2
    elif prop_down > 80:
        direction = 1
    print(prop_up, "% of price values are over the SMA.")
    return(direction)

detect_trend(prices, data)


# macd
macd, meta_macd = globalenv.ti.get_macd(symbol='ZM', interval='1min', series_type='close')
macd = macd[macd.index.day == 1]
macd = macd[macd.index.hour >= 14]
macd = macd[macd.index.hour < 15]

def detect_momentum(macd_data):
    """ momentum = 0 => no clear momentum
        momentum = 1 => downward momentum
        momentum = 2 => upward momentum """
    momentum = 0
    prop_up = round(sum(macd_data > 0) / len(macd_data) * 100, 2)
    prop_down = round(sum(macd_data < 0) / len(macd_data) * 100, 2)
    if prop_up > 75:
        momentum = 2
    elif prop_down > 75:
        momentum = 1
    print(prop_up, "% of macd values are positive.")
    return(momentum)

detect_momentum(macd.MACD)


# RSI
rsi, meta_rsi = globalenv.ti.get_rsi(symbol='ZM', interval='1min', series_type='close')
rsi = rsi[rsi.index.day == 1]
rsi = rsi[rsi.index.hour >= 14]
rsi = rsi[rsi.index.hour < 15]

figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
plt.plot(rsi)
plt.tight_layout()
plt.grid()
plt.show()

def detect_revearsal(prices, sma_data, rsi_data):
    """ revearsal = 0 => no revearsal
        revearsal = 2 => possible revearsal (up to downtrend) starting soon
        revearsal = 1 => possible revearsal (down to uptrend) starting soon"""
    revearsal = 0
    lowerbound = 30
    upperbound = 70
    prop_up = round(sum(rsi_data > upperbound) / len(rsi_data) * 100, 2)
    prop_down = round(sum(rsi_data < lowerbound) / len(rsi_data) * 100, 2)
    if prop_up > 75:
        revearsal = 2
        print("Security is becoming overbought (overvalued).")
    elif prop_down > 75:
        revearsal = 1
        print("Security is becoming oversold (undervalued).")
    return(revearsal)

detect_revearsal(prices, data.SMA, rsi.RSI)



# pattern detection
m = fbprophet.Prophet(changepoint_prior_scale=0.05)
# The higher the changepoint prior scale, the more flexible the model
m.fit(data)

# Make a future dataframe for 2 year
data_forecast = m.make_future_dataframe(periods=10, freq='min')
# Make predictions
gm_forecast = m.predict(data_forecast)


# Python
fig = m.plot_components(gm_forecast)

# Points where growth rate significantly changes
m.changepoints


# Plot the search frequency
figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
m.plot(gm_forecast)
plt.tight_layout()
plt.vlines(m.changepoints, ymin = 113, ymax= 120, colors = 'r', linewidth=0.6, linestyles = 'dashed', label = 'Changepoints')
plt.show()


smoothing = 10
smooth_prices = data.y.rolling(window=smoothing).mean().dropna()
simple_plot(pd.DataFrame(smooth_prices))


simple_plot(data)


sub_data = data[85:]
sub_data.reset_index(inplace=True, drop=True)
sub_data.y.plot()



# Finding minima and maxima
def get_minmax(prices_df, smoothing = 2, window_range = 2):
    # smooth to find local min max
    smooth_prices = prices_df['y'].rolling(window=smoothing).mean().dropna()
    simple_plot(pd.DataFrame(smooth_prices))
    local_max = argrelextrema(smooth_prices.values, np.greater)[0]
    local_min = argrelextrema(smooth_prices.values, np.less)[0]

    price_local_max_dt = []
    for i in local_max:
        if (i > window_range) and (i < len(prices_df) - window_range):
            price_local_max_dt.append(
                prices_df.iloc[i-window_range:i+window_range]['y'].idxmax()
                )

    price_local_min_dt = []
    for i in local_min:
        if (i > window_range) and (i < len(prices_df) - window_range):
            price_local_min_dt.append(
                prices_df.iloc[i-window_range:i+window_range]['y'].idxmin()
                )

    maxima = pd.DataFrame(prices_df.loc[price_local_max_dt])
    minima = pd.DataFrame(prices_df.loc[price_local_min_dt])
    max_min = pd.concat([maxima, minima]).sort_index()
    max_min = max_min[~max_min.index.duplicated()]

    maxima = pd.DataFrame(prices_df.loc[local_max])
    minima = pd.DataFrame(prices_df.loc[local_min])
    max_min = pd.concat([maxima, minima]).sort_index()
    max_min = max_min[~max_min.index.duplicated()]

    # plot
    figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
    prices_df['y'].plot()
    plt.scatter(max_min.index, max_min.y.values, color='orange', alpha=.5)
    plt.tight_layout()
    plt.grid()
    plt.show()

    return(max_min)

figure(num=None, figsize=(6, 4), dpi=80, facecolor='w', edgecolor='k')
prices_df['y'].plot()
plt.scatter(max_min.index, max_min.y.values, color='orange', alpha=.5)
plt.tight_layout()
plt.grid()
plt.show()


prices_df = pd.DataFrame(data['4. close'])
prices_df.reset_index(inplace=True, drop=True)
minmax = get_minmax(prices_df, smoothing = 3, window_range = 2)


prices_df = sub_data



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


# Resistance and support identification
