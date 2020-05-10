########################################################
################# PORTFOLIO MANAGEMENT #################
########################################################

### IMPORTATION ###
import pytz
from datetime import datetime
from datetime import timedelta

### GLOBAL ENV ###
timezone = pytz.timezone("America/New_York")
ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
portname = str(ny_now.year) + '-' + str(ny_now.month) + '-' + str(ny_now.day)


### FUNCTIONS ###
def prepare_portfolio(portfolio):
    portfolio[portname] = {"bought":{}, "owned":{}, "sold":{}}
    return(portfolio)


def add_purchase(portfolio, index, five_eq_symbols, five_eq_data):
    symbol = five_eq_symbols[index]
    print("Buying", symbol)
    eq_data = five_eq_data[index].tail(1)

    # get the stock state using the symbol
    stock_state = { 'close':    eq_data['4. close'][0],
                    'high':     eq_data['2. high'][0],
                    'low':      eq_data['3. low'][0],
                    'name':     symbol,
                    'open':     eq_data['1. open'][0],
                    'volume':   eq_data['5. volume'][0]
    }

    # how many times have we traded this stock
    tmp = portfolio[portname]['bought']
    if tmp == {}:
        ith_time_bought = 0
    else:
        ith_time_bought = [tmp[key]['name'] for key in tmp].count(symbol)

    # adding purchase in 'bought' and 'owned'
    portfolio[portname]['bought'][symbol + " " + str(ith_time_bought)] = stock_state
    portfolio[portname]['owned'][symbol + " " + str(ith_time_bought)] = stock_state

    return(portfolio)


def add_sale(portfolio, index, five_eq_symbols, five_eq_data):
    symbol = five_eq_symbols[index]
    print("Selling", symbol)
    eq_data = five_eq_data[index].tail(1)

    # get the stock state using the symbol
    stock_state = { 'close':    eq_data['4. close'][0],
                    'high':     eq_data['2. high'][0],
                    'low':      eq_data['3. low'][0],
                    'name':     symbol,
                    'open':     eq_data['1. open'][0],
                    'volume':   eq_data['5. volume'][0]
    }

    # how many times have we traded this stock
    tmp = portfolio[portname]['sold']
    if tmp == {}:
        ith_time_sold = 0
    else:
        ith_time_sold = [tmp[key]['name'] for key in tmp].count(symbol)

    # adding purchase in 'sold' and removing from 'owned'
    portfolio[portname]['sold'][symbol + " " + str(ith_time_sold)] = stock_state
    del portfolio[portname]['owned'][symbol + " " + str(ith_time_sold)]

    return(portfolio)


def add_purchases(portfolio, booleans, five_eq_symbols, five_eq_data):
    indexes_to_purchase = [i for i in range(len(booleans)) if booleans[i] == True]
    for index in indexes_to_purchase:
        add_purchase(portfolio, index, five_eq_symbols, five_eq_data)


def add_sales(portfolio, booleans, five_eq_symbols, five_eq_data):
    indexes_to_purchase = [i for i in range(len(booleans)) if booleans[i] == True]
    for index in indexes_to_purchase:
        add_sale(portfolio, index, five_eq_symbols, five_eq_data)


def compute_profit(portfolio):
    profit = 0
    sold = portfolio[portname]['sold']
    bought = portfolio[portname]['bought']

    purchases = [bought[key]['name'] for key in bought]
    for symbol in sold:
        name = sold[symbol]['name']
        close_sold = sold[symbol]['close']
        if name in purchases:
            close_bought = bought[symbol]['close']
            profit += (close_bought - close_sold)

    return(profit)


def do_we_currently_own(symbol, portfolio):
    boolean = False
    owned_secus = [portfolio[portname]['owned'][key]['name'] for key in portfolio[portname]['owned']]
    if symbol in owned_secus:
        boolean = True
    return(boolean)
