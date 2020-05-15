"""
TRADING BOT - 04 / 2020

@author: guillemforto
To launch it via Terminal:
    > cd /Users/guillemforto/Desktop/trading-bot
    > python main.py
"""


### GLOBAL ENV ###
from globalenv import *
    # modules #
import time_management as tm
import data_retrieval as dr
import portfolio_management as pm
import strategy as strat

### GLOBAL VARS ###
real_time_tickers = {   'IBM' : 'International Business Machines',
                        'CAT':  'Caterpillar',
                        'KO':   'Coca-cola',
                        'HPQ':  'Hewlett Packard',
                        'JNJ':  'Johnson & Johnson',
                        'MTW':  'Manitowoc',
                        'SNAP': 'Snapchat',
                        'MO':   'Altria',
                        'FCX':  'Freeport',
                        'HLF':  'Herbalife',
                        'PRGO': 'Perrigo',
                        'BABA': 'Alibaba',
                        'JPM':  'JPMorgan',
                        'V':    'Visa Inc.',
                        'WMT':  'Walmart Inc.',
                        'XOM':  'Exxon Mobil',
                        'BAC':  'Bank of America',
                        'PG':   'The Procter & Gamble Co',
                        'T':    'AT&T',
                        'MA':   'Mastercard',
                        'VZ':   'Verizon',
                        'DIS':  'Walt Disney'}
max_nb_requests_per_day = 500 - len(real_time_tickers)
max_nb_requests_per_minute = 5
timezone = pytz.timezone("America/New_York")



def main():
    print("\n \n                  WELCOME TO GUILLEM'S TRADING BOT! \n \n")
    ### PRE-trading ###
    nyse_h = tm.get_next_trading_hours()
    startTrading = tm.is_market_open(nyse_h)

    firstEntrance = True
    while startTrading == False:
        secs_till_op = tm.get_secs_till_op(nyse_h)
        if firstEntrance == True:
            time_till_op = round((secs_till_op / 60) / 60, 2)
            hours_till_op = int(time_till_op)
            minutes_till_op = int((time_till_op - hours_till_op) * 60)
            print("Market opens in", hours_till_op, "hours,", minutes_till_op, "minutes.")
            print("We will wait till then before starting.")
            firstEntrance = False

        if secs_till_op % 300 == 0 and secs_till_op != 0:
            time_till_op = round((secs_till_op / 60) / 60, 2)
            hours_till_op = int(time_till_op)
            minutes_till_op = int((time_till_op - hours_till_op) * 60)
            print(hours_till_op, 'h', minutes_till_op, 'mins to go', sep='')
        time.sleep(1)
        startTrading = secs_till_op == 0
        # startTrading = True


    ### TRADING ###
    while startTrading:
        today_we_traded = False
        ### PREPARATION ###
        print("Market is open! Waiting 1 min before starting...\n")
        time.sleep(60)

        print("First of all, let's pick the equities we will be looking at:")
        candidates_table = dr.get_candidate_equities()
        (eq_symbols, eq_data, eq_supres) = dr.get_5_equities_data(candidates_table)

        if len(eq_symbols) == 0:
            print("No suitable equities were found on which to trade. Try again tomorrow, thank you! \n")
            break
        else:
            today_we_traded = True

        portfolio = pm.prepare_portfolio()
        stoploss_orders = {}
        nb_equities = len(eq_symbols)
        requests_frequency = tm.get_requests_frequency(nyse_h, nb_equities)
        requests_frequency_inmin = math.ceil(requests_frequency / 60)


        ### ACTION ###
        action = True
        while action == True:
            retrieve = tm.is_moment_to_retrieve(nyse_h, requests_frequency)
            while retrieve == False:
                # __ seconds till next retrieval
                time.sleep(1)
                retrieve = tm.is_moment_to_retrieve(nyse_h, requests_frequency)

            try:
                eq_data = dr.update_5_equities_data(eq_symbols)
            except:
                print("Couldn't retrieve anymore data")
                break

            print("Checking for new trading opportunities...")
            (golong_booleans, coverlong_booleans) = \
                strat.go_or_cover_long(eq_symbols, eq_data, eq_supres, portfolio, requests_frequency_inmin)

            if any(golong_booleans):
                pm.add_purchases(portfolio, golong_booleans, eq_symbols, eq_data)
                pm.place_stoploss_orders(portfolio, stoploss_orders, eq_symbols, eq_supres)
                print('stoploss_orders', stoploss_orders)
                curr_proloss = pm.compute_profit(portfolio)
                print("Our current profit / loss is:", curr_proloss, '€')
                mailing.send_email(portfolio, profitloss_flt = curr_proloss)
            else:
                print('\nNothing to buy.')

            if any(coverlong_booleans):
                pm.add_sales(portfolio, coverlong_booleans, eq_symbols, eq_data)
                curr_proloss = pm.compute_profit(portfolio)
                print("Our current profit / loss is:", curr_proloss, '€')
                mailing.send_email(portfolio, profitloss_flt = curr_proloss)
            else:
                print("Nothing to sell.\n")

            print('Portfolio:', portfolio)
            print("Done!\n")

            action = tm.is_market_open(nyse_h)


        startTrading = tm.is_market_open(nyse_h)

    if today_we_traded:
        print("The day is ended!\n")
        print("FINAL PROFIT / LOSS:", pm.compute_profit(portfolio), '\n')


if __name__ == "__main__":
    main()
