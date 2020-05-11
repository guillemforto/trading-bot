#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRADING BOT

@author: guillemforto
To launch it via Terminal:
cd /Users/guillemforto/Desktop/trading-bot
python main.py
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

from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators


### MODULES ###
import time_management as tm
import data_retrieval as dr
import portfolio_management as pm
import strategy as strat


### GLOBAL ENV ###
    # time
# max_nb_requests_per_day = 400
# max_nb_requests_per_minute = 5

    # alphavantage api
apikey = '0FA4MXDSORI7KI96'
ts = TimeSeries(key=apikey, output_format='pandas')
ti = TechIndicators(key=apikey)


### PARAMETERS ###
url = 'https://finance.yahoo.com/gainers?count=100&offset=0'
init_capital = 1000



def main():
    print("\n \n                  WELCOME TO GUILLEM'S TRADING BOT! \n \n")
    ### PRE-trading ###
    nyse_h = tm.get_next_trading_hours()
    requests_frequency = tm.get_requests_frequency(nyse_h)
    startTrading = tm.is_market_open(nyse_h)

    firstEntrance = True
    while startTrading == False:
        secs_till_op = tm.get_secs_till_op(nyse_h)
        time_till_op = round((secs_till_op / 60) / 60, 2)
        hours_till_op = int(time_till_op)
        minutes_till_op = int((time_till_op - hours_till_op) * 60)
        if firstEntrance == True:
            print("Market opens in", hours_till_op, "hours,", minutes_till_op, "minutes.")
            print("We will wait till then before starting.")
            firstEntrance = False
        if secs_till_op % 300 == 0 and secs_till_op != 0:
            print(hours_till_op, ':', minutes_till_op, ' to go', sep='')
        time.sleep(1)
        startTrading = secs_till_op == 0


    ### TRADING ###
    while startTrading:
        ### PREPARATION ###
        print("Market is open! Waiting 120 seconds before starting...\n")
        # time.sleep(120)

        print("First of all, let's pick the equities we will be looking at:")
        candidates_table = dr.get_candidate_equities(url)
        (five_eq_symbols, five_eq_data, five_eq_supres) = dr.get_5_equities_data(candidates_table)

        portfolio = pm.prepare_portfolio(dict())


        ### ACTION ###
        action = True
        while action == True:
            retrieve = tm.is_moment_to_retrieve(nyse_h, requests_frequency)
            while retrieve == False:
                # __ seconds till next retrieval
                time.sleep(1)
                retrieve = tm.is_moment_to_retrieve(nyse_h, requests_frequency)

            five_eq_data = dr.update_5_equities_data(five_eq_symbols)

            print("Checking for new trading opportunities...")
            booleans = strat.is_moment_to_golong(five_eq_symbols, five_eq_data, five_eq_supres, portfolio)
            if any(booleans):
                pm.add_purchases(portfolio, booleans, five_eq_symbols, five_eq_data)
                print("Our current profit / loss is:", pm.compute_profit(portfolio), '€')
            else:
                print('Nothing to buy.')

            booleans = strat.is_moment_to_coverlong(five_eq_symbols, five_eq_data, five_eq_supres, portfolio)
            if any(booleans):
                pm.add_sales(portfolio, booleans, five_eq_symbols, five_eq_data)
                print("Our current profit / loss is:", pm.compute_profit(portfolio), '€')
            else:
                print("Nothing to sell.")
            print("Done!\n")

            action = tm.is_market_open(nyse_h)

        startTrading = tm.is_market_open(nyse_h)

    print("The day is ended!\n")
    print("FINAL PROFIT / LOSS:", pm.compute_profit(portfolio))


if __name__ == "__main__":
    main()
