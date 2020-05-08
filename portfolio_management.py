########################################################
################# PORTFOLIO MANAGEMENT #################
########################################################

### IMPORTATION ###
import pytz
from datetime import datetime
from datetime import timedelta

### GLOBAL ENV ###
timezone = pytz.timezone("America/New_York")


### FUNCTIONS ###
def prepare_portfolio_for_day(portfolio):
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    name = str(ny_now.year) + '-' + str(ny_now.month) + '-' + str(ny_now.day)
    portfolio[name] = {"bought":{}, "owned":{}, "sold":{}}
    return(portfolio)


def add_purchase(symbol, portfolio):
    print("Buying", symbol)
    # get the stock state using the symbol
    stock_state = { 'close':    44,
                    'high':     45,
                    'low':      43,
                    'name':     symbol,
                    'opening':  43.5,
                    'volume':   8888
    }
    # how many times have we traded this stock
    tmp = portfolio[name]['bought']
    if tmp == {}:
        ith_time_bought = 0
    else:
        ith_time_bought = [tmp[key]['name'] for key in tmp].count(symbol)

    # adding purchase in 'bought' and 'owned'
    portfolio[name]['bought'][symbol + " " + str(ith_time_bought)] = stock_state
    portfolio[name]['owned'][symbol + " " + str(ith_time_bought)] = stock_state

    return(portfolio)


def add_sale(symbol, portfolio):
    print("Selling", symbol)
    # get the stock state using the symbol
    stock_state = { 'close':    44,
                    'high':     45,
                    'low':      43,
                    'name':     symbol,
                    'opening':  43.5,
                    'volume':   8888
    }
    # how many times have we traded this stock
    tmp = portfolio[name]['sold']
    if tmp == {}:
        ith_time_sold = 0
    else:
        ith_time_sold = [tmp[key]['name'] for key in tmp].count(symbol)

    # adding purchase in 'sold' and removing from 'owned'
    portfolio[name]['sold'][symbol + " " + str(ith_time_sold)] = stock_state
    del portfolio[name]['owned'][symbol + " " + str(ith_time_sold)]

    return(portfolio)


def compute_profit(portfolio):
    profit = 0
    sold = portfolio[name]['sold']
    bought = portfolio[name]['bought']

    purchases = [bought[key]['name'] for key in bought]
    for symbol in sold:
        name = sold[symbol]['name']
        close_sold = sold[symbol]['close']
        if name in purchases:
            close_bought = bought[symbol]['close']
            profit += (close_bought - close_sold)

    return(profit)
