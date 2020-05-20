########################################################
################# PORTFOLIO MANAGEMENT #################
########################################################

### IMPORTATION ###
import globalenv
from globalenv import *


### FUNCTIONS ###
def qtty_shares(cl_price, eq_symbols, init_capital):
    budget = init_capital / len(eq_symbols)
    return(budget // cl_price)


def times_stock_been_traded(portfolio, operation, symbol):
    tmp = portfolio[operation]
    ith_time_bought = 0
    if tmp != {}:
        ith_time_bought = [tmp[key]['name'] for key in tmp].count(symbol)
    return(ith_time_bought)


def add_purchase(portfolio, index, eq_symbols, eq_data, init_capital):
    symbol = eq_symbols[index]
    print('\nTrading opportunity detected!')
    print("We go long on", symbol)
    eq_data = eq_data[index].tail(1)

    # get the stock state using the symbol
    buy_price = eq_data['4. close'][0]
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(globalenv.timezone)
    curr_day = str(ny_now.year) + '-' + str(ny_now.month) + '-' + str(ny_now.day)
    purchase_chars = {  'name':     symbol,
                        'close':    buy_price,
                        'quantity': qtty_shares(buy_price, eq_symbols, init_capital),
                        'day':      curr_day,
                        'high':     eq_data['2. high'][0],
                        'low':      eq_data['3. low'][0],
                        'open':     eq_data['1. open'][0],
                        'volume':   eq_data['5. volume'][0]
    }
    print("Closing price at which we buy:", buy_price, '$')
    print("How many shares do we buy:", purchase_chars['quantity'], '\n')

    # how many times have we traded this stock
    ith_time_bought = times_stock_been_traded(portfolio, 'bought', symbol)

    # adding purchase in 'bought' and 'owned'
    portfolio['bought'][symbol + " " + str(ith_time_bought)] = purchase_chars
    portfolio['owned'][symbol + " " + str(ith_time_bought)] = purchase_chars
    return(portfolio)


def add_sale(portfolio, index, eq_symbols, eq_data, init_capital):
    symbol = eq_symbols[index]
    print("\nCovering long position for ", symbol, ".", sep='')
    eq_data = eq_data[index].tail(1)

    # get the stock state using the symbol
    sell_price = eq_data['4. close'][0]
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(globalenv.timezone)
    curr_day = str(ny_now.year) + '-' + str(ny_now.month) + '-' + str(ny_now.day)
    sale_chars = {  'name':     symbol,
                    'close':    sell_price,
                    'quantity': qtty_shares(sell_price, eq_symbols, init_capital),
                    'day':      curr_day,
                    'high':     eq_data['2. high'][0],
                    'low':      eq_data['3. low'][0],
                    'open':     eq_data['1. open'][0],
                    'volume':   eq_data['5. volume'][0]
    }
    print("Closing price at which we sell:", sell_price, '$')
    print("How many shares do we buy:", sale_chars['volume'], '\n')

    # how many times have we traded this stock
    ith_time_sold = times_stock_been_traded(portfolio, 'sold', symbol)

    # adding purchase in 'sold' and removing from 'owned'
    portfolio['sold'][symbol + " " + str(ith_time_sold)] = sale_chars
    del portfolio['owned'][symbol + " " + str(ith_time_sold)]
    return(portfolio)


def add_purchases(portfolio, golong_booleans, eq_symbols, eq_data, init_capital):
    indexes_to_purchase = [i for i in range(len(golong_booleans)) if golong_booleans[i] == True]
    for index in indexes_to_purchase:
        add_purchase(portfolio, index, eq_symbols, eq_data, init_capital)


def add_sales(portfolio, coverlong_booleans, eq_symbols, eq_data, init_capital):
    indexes_to_sale = [i for i in range(len(coverlong_booleans)) if coverlong_booleans[i] == True]
    for index in indexes_to_sale:
        add_sale(portfolio, index, eq_symbols, eq_data, init_capital)


def do_we_currently_own(symbol, portfolio):
    boolean = False
    owned_secus = [portfolio['owned'][key]['name'] for key in portfolio['owned']]
    if symbol in owned_secus:
        boolean = True
    return(boolean)


def place_stoploss_orders(portfolio, stoploss_orders, eq_symbols, eq_supres):
    """If we went long on a support, we prevent from downside breakout by placing
    the stop loss order just below the support level (i.e. at support - margin)"""
    owned = portfolio['owned']
    owned_symbols = [owned[key]['name'] for key in owned]
    for symbol in owned_symbols:
        index = eq_symbols.index(symbol)
        (support_value, resistance_value, margin) = eq_supres[i]
        stoploss_orders[symbol] = support_value - (margin / 5)
    return(stoploss_orders)


def place_halfprofit_orders(portfolio, halfprofit_orders, eq_symbols, eq_supres):
    """If we went long on a support, we lock in a profit by placing a halfprofit
    order in-between support and resistance (i.e. at (resistance + support) / 2))"""
    owned = portfolio['owned']
    owned_symbols = [owned[key]['name'] for key in owned]
    for symbol in owned_symbols:
        index = eq_symbols.index(symbol)
        (support_value, resistance_value, margin) = eq_supres[i]
        halfprofit_orders[symbol] = (support_value + resistance_value) / 2
    return(halfprofit_orders)


def compute_profit(portfolio, init_capital):
    profit = init_capital
    sold = portfolio['sold']
    bought = portfolio['bought']
    for key in sold:
        if key in bought.keys():
            close_sold = sold[key]['close']
            quantity_sold = sold[key]['quantity']
            close_bought = bought[key]['close']
            quantity_bought = bought[symbol]['quantity']
            profit += (quantity_sold * close_sold - quantity_bought * close_bought)
    return(round(profit, 2))
