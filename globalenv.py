### PACKAGES ###
import sys
import os

import numpy as np
import pandas as pd
import math
import statistics
from scipy.signal import argrelextrema

import tqdm

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
import portfolio_management as pm
import time_management as tm
import strategy as strat
import mailing


### CONSTANT GLOBAL VARIABLES ###
    # alphavantage
from usersettings import *
ts = TimeSeries(key=usersettings.apikey, output_format='pandas')
ti = TechIndicators(key=usersettings.apikey)

    # candidate stocks for which we can obtain real-time data
real_time_tickers = {\
    'IBM' : 'International Business Machines',              'CAT':  'Caterpillar',
    'KO':   'Coca-cola',                                    'HPQ':  'Hewlett Packard',
    'JNJ':  'Johnson & Johnson',                            'MTW':  'Manitowoc',
    'SNAP': 'Snapchat',                                     'MO':   'Altria',
    'FCX':  'Freeport',                                     'HLF':  'Herbalife',
    'PRGO': 'Perrigo',                                      'BABA': 'Alibaba',
    'JPM':  'JPMorgan',                                     'V':    'Visa Inc.',
    'WMT':  'Walmart Inc.',                                 'XOM':  'Exxon Mobil',
    'BAC':  'Bank of America',                              'PG':   'The Procter & Gamble Co',
    'T':    'AT&T',                                         'MA':   'Mastercard',
    'ANF' : 'Abercrombie & Fitch',                          'ACN':   'Accenture',
    'BIO' : 'Bio-Rad Laboratories',                         'HTZ' : 'Hertz Global Holdings',
    'GE'  : 'Gen Electric',                                 'DAL' : 'Delta Air Lines',
    'F'   : 'Ford Motor',                                   'CCL' : 'Carnival',
    'M'   : 'Macys',                                        'WFC' : 'Wells Fargo',
    'LUV' : 'Southwest Airlines',                           'MGM' : 'Mirage',
    'C'   : 'Citigroup',                                    'AUY' : 'Yamana Gold Inc.',
    'RCL' : 'Royal Caribbean Cr',                           'BA'  : 'Boeing',
    'OXY' : 'Occidental Pet',                               'MS'  : 'Morgan Stanley',
    'DIS' : 'Walt Disney',                                  'HAL' : 'Halliburton',
    'FCX' : 'Freeport Mcmoran',                             'CCL' : 'Exxon Mobil',
    'VZ'  : 'Verizon',                                      'JWN' : 'Nordstrom',
    'CTL' : 'Centurytel',                                   'IBN' : 'Icici Bank',
    'SLB' : 'Schlumberger',                                 'KEY' : 'Keycorp',
    'UA'  : 'Under Armour',                                 'HBI' : 'Hanesbrands',
    'RF'  : 'Regions',                                      'MRK' : 'Merck (pharmaceutical)',
    'ING' : 'Ing (banking)',                                'AA'  : 'Alcoa (aluminium producer)',
    'GGB' : 'Gerdau (steel producer)',                      'USB' : 'Us Bancorp (banking)',
    'SWN' : 'Southwestern Energy (gas producer)',           'CIM' : 'Chimera Investment (Real Estate Investor)',
    'SPG' : 'Simon Property Group (Real Estate Investor)',  'KR'  : 'Kroger (Retail company)',
    'KIM' : 'Kimco (Real State Investor)',                  'AXP' : 'American Express (financial services)',
    'CBL' : 'CBL Properties (Real Estate Investor)'}

    # general
timezone = pytz.timezone("America/New_York")
max_nb_requests_per_day = 500 - len(real_time_tickers)
print_color = {
    'PURPLE' : '\033[95m',
    'CYAN' : '\033[96m',
    'DARKCYAN' : '\033[36m',
    'BLUE' : '\033[94m',
    'GREEN' : '\033[92m',
    'YELLOW' : '\033[93m',
    'RED' : '\033[91m',
    'BOLD' : '\033[1m',
    'UNDERLINE' : '\033[4m',
    'END' : '\033[0m'
}
