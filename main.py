#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRADING BOT

@author: guillemforto
"""


### IMPORTATION ###
import numpy as np
import pandas as pd
import math
from scipy.signal import argrelextrema

import requests

from datetime import datetime
from datetime import timedelta
import time
import pytz

from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators


### MODULES ###
import time_management as tm
import data_retrieval as dr
import portfolio_management as pm
# import strategy as strat


### GLOBAL ENV ###
    # time
timezone = pytz.timezone("America/New_York")
max_nb_requests_per_day = 500
max_nb_requests_per_minute = 5

    # alphavantage api
apikey = '0FA4MXDSORI7KI96'
ts = TimeSeries(key=apikey, output_format='pandas')
ti = TechIndicators(key=apikey)


### PARAMETERS ###
capital_inicial = 1000
nb_equities = 5




### MAIN ###
def main():
    # PRE-TRADING
    nyse_h = tm.get_next_trading_hours()
    requests_frequency = tm.get_requests_frequency(nyse_h)
    startTrading = tm.is_market_open(nyse_h)

    if startTrading == False:
        secs_till_op = tm.get_secs_till_op(nyse_h)
        # time.sleep(secs_till_op)
        startTrading = True


    # TRADING
    while startTrading:
        print("Market is open! Waiting 30 seconds before starting...")
        time.sleep(30)

        url = 'https://finance.yahoo.com/gainers'
        candidates_table = dr.get_candidate_equities(url)
        (five_eq_symbols, five_eq_data) = dr.get_5_equities_data(candidates_table)

        portfolio = pm.create_portfolio(five_eq_symbols)

        operate = tm.is_moment_to_retrieve(nyse_h, requests_frequency)
        while operate == False:
            time.sleep(1)
            operate = tm.is_moment_to_retrieve(nyse_h, requests_frequency)
        else:
            any_trades = False
            print("GO")
            operate = False

            # update portfolio
            if any_trades == True:
                pm.add_purchase(portfolio)
                pm.add_sale(portfolio)

        startTrading = tm.is_market_open(nyse_h)

    print("The day is ended!")


if __name__ == "__main__":
    main()
