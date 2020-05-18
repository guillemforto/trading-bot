### PACKAGES ###
import sys
import os

import numpy as np
import pandas as pd
import math
import statistics
from scipy.signal import argrelextrema

from tqdm import tqdm

import requests

from datetime import datetime
from datetime import timedelta
import time
import pytz
import calendar
import holidays

from string import Template

import trendln
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib, ssl


### MODULES ###
import data_retrieval as dr
import mailing
import portfolio_management as pm
import time_management as tm
import strategy as strat


### CONSTANT GLOBAL VARIABLES ###
    # general
timezone = pytz.timezone("America/New_York")
init_capital = np.float(input("What's your initial investment (in $)?\n> "))

    # alphavantage
apikey = '0FA4MXDSORI7KI96'
ts = TimeSeries(key=apikey, output_format='pandas')
ti = TechIndicators(key=apikey)

    # mailing
smtp_server = "smtp.gmail.com"
sender_email = "tradingbot.guillem@gmail.com"
password = 'cekqer-2hyPsu-nerrev'
receiver_email = "gforto@gmail.com"

    # candidate stocks for which we can obtain real-time data
real_time_tickers = {\
    'IBM' : 'International Business Machines',  'CAT':  'Caterpillar',
    'KO':   'Coca-cola',                        'HPQ':  'Hewlett Packard',
    'JNJ':  'Johnson & Johnson',                'MTW':  'Manitowoc',
    'SNAP': 'Snapchat',                         'MO':   'Altria',
    'FCX':  'Freeport',                         'HLF':  'Herbalife',
    'PRGO': 'Perrigo',                          'BABA': 'Alibaba',
    'JPM':  'JPMorgan',                         'V':    'Visa Inc.',
    'WMT':  'Walmart Inc.',                     'XOM':  'Exxon Mobil',
    'BAC':  'Bank of America',                  'PG':   'The Procter & Gamble Co',
    'T':    'AT&T',                             'MA':   'Mastercard',
    'ANF':  'Abercrombie & Fitch',              'ACN':   'Accenture'}
