"""
TRADING BOT - April 2020

@author: guillemforto
To launch it via Terminal:
    > cd /Users/guillemforto/github/trading-bot
    > python main.py
"""

### GLOBAL ENV ###
from globalenv import *
import globalenv


### GLOBAL VARS ###
portfolio = {"bought": dict(), "owned": dict(), "sold": dict()}
stoploss_orders = dict()
halfprofit_orders = dict()

def main():
    print("\n\n\n                  WELCOME TO GUILLEM'S TRADING BOT! \n\n\n")
    init_capital = np.float(input("What's your initial investment for this simulation (in $)?\n> "))
    nb_days = np.float(input("During how many trading days would you like to run the bot?\n> "))
    print('')
    ith_day = 1
    while ith_day <= nb_days:

        ### PRE-trading ###
        nyse_h = tm.get_next_trading_hours()
        startTrading = tm.is_market_open(nyse_h)

        if startTrading == False:
            secs_till_op = tm.get_secs_till_op(nyse_h)
            hours_till_op, minutes_till_op = tm.get_time_measures(secs_till_op)
            print("Market opens in", hours_till_op, "hours,", minutes_till_op, "minutes.")
            print("We will wait till then before starting.")

        while startTrading == False:
            secs_till_op = tm.get_secs_till_op(nyse_h)
            if secs_till_op % 300 == 0 and secs_till_op != 0:
                hours_till_op, minutes_till_op = tm.get_time_measures(secs_till_op)
                print(hours_till_op, 'h', minutes_till_op, 'mins to go', sep='')
            time.sleep(1)
            startTrading = secs_till_op == 0
            # startTrading = True


        ### TRADING ###
        while startTrading == True:
            today_we_traded = False

            ### PREPARATION ###
            print("Market is open! Waiting 2 mins before starting...\n")
            time.sleep(90)
                # equity selection
            if ith_day == 1:
                print("First of all, let's pick the equities we will be looking at:")
                candidates_table = dr.get_candidate_equities()
                (eq_symbols, eq_data, eq_supres) = dr.get_5_equities_data(candidates_table)

            if len(eq_symbols) != 0:
                today_we_traded = True
                ith_day += 1
            else:
                print("No suitable equities were found on which to trade.")
                break

            nb_equities = len(eq_symbols)
            requests_frequency = tm.get_requests_frequency(nyse_h, nb_equities)


            ### ACTION ###
            action = True
            while action == True:
                # Retrieval
                retrieve = tm.is_moment_to_retrieve(nyse_h, requests_frequency)
                while retrieve == False:
                    time.sleep(1)
                    retrieve = tm.is_moment_to_retrieve(nyse_h, requests_frequency)
                try:
                    eq_data = dr.update_5_equities_data(eq_symbols)
                except:
                    print("Couldn't retrieve anymore data.")
                    break

                print("Checking for new trading opportunities:")
                (coverlong_booleans, golong_booleans) = \
                    strat.go_or_cover_long(eq_symbols, eq_data, eq_supres, portfolio, stoploss_orders, halfprofit_orders, requests_frequency_inmin = math.ceil(requests_frequency / 60))


                if any(coverlong_booleans):
                    pm.add_sales(portfolio, coverlong_booleans, eq_symbols, eq_data, init_capital)
                else:
                    print('\nNothing to sell.')

                if any(golong_booleans):
                    pm.add_purchases(portfolio, golong_booleans, eq_symbols, eq_data, init_capital)
                    pm.place_stoploss_orders(portfolio, stoploss_orders, eq_symbols, eq_supres)
                    pm.place_halfprofit_orders(portfolio, halfprofit_orders, eq_symbols, eq_supres)
                    print('Stoploss orders:', stoploss_orders)
                    print('Halfprofit orders:', halfprofit_orders)
                else:
                    print('Nothing to buy.\n')

                if any(golong_booleans) or any(coverlong_booleans):
                    curr_proloss = pm.compute_profit(portfolio, init_capital)
                    print("\nOur current profit / loss is:", curr_proloss, '$\n')
                    mailing.send_email(portfolio, curr_proloss)

                print('Portfolio:', portfolio)
                print(globalenv.print_color['YELLOW'] + 'Done!' + globalenv.print_color['END'] + '\n')
                action = tm.is_market_open(nyse_h)


            startTrading = tm.is_market_open(nyse_h)

        # out of the two first whiles
        print("The day is ended!\n")
        if today_we_traded:
            print("FINAL PROFIT / LOSS:", pm.compute_profit(portfolio, init_capital), '$\n')
            time.sleep(10)




if __name__ == "__main__":
    main()
