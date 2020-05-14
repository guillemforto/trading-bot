### IMPORTATION ###
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

import trendln
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure

import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.techindicators import TechIndicators


### MODULES ###
import time_management as tm
import data_retrieval as dr
import portfolio_management as pm
import strategy as strat
