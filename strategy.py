########################################################
################### TRADING STRATEGY ###################
########################################################

### IMPORTATION ###
from globalenv import *
# import pattern_detection as patdet


### FUNCTIONS ###
# def setup_is_present():
#     boolean = False
#     if detect_trend(prices, sma_data) == 2:
#         boolean = True
#     return(boolean)


def is_moment_to_golong(index, symbol, closing_prices, support_value, margin, golong_booleans, portfolio):
    """We go long if:
    - we don't own the stock + price is close to support (i.e. if price breaches sup + margin)"""
    if not pm.do_we_currently_own(symbol, portfolio):
        if any([k - margin <= support_value for k in closing_prices]):
            golong_booleans[index] = True
            print('- Last closing prices:', closing_prices)
            print("- Today's (support + margin) value:", round(support_value + margin, 2), '\n')
    return(golong_booleans)


def is_moment_to_coverlong(index, symbol, closing_prices, resistance_value, margin, coverlong_booleans, golong_booleans, portfolio, stoploss_orders, halfprofit_orders):
    """We cover long if:
    - we own the stock + price is close to resistance (i.e. if price breaches res - margin)
    - we own the stock + price breaches a stop-loss order (i.e. in case of a downside breakout)
    - we own the stock + price breaches a half-profit order"""
    if pm.do_we_currently_own(symbol, portfolio):
        if any([k + margin >= resistance_value for k in closing_prices]):
            coverlong_booleans[index] = True
            print('- Last closing prices:', closing_prices)
            print("- Today's (resistance - margin) values:", round(resistance_value - margin, 2), '\n')
        elif any([k <= stoploss_orders[symbol] for k in closing_prices]):
            coverlong_booleans[index] = True
            print('- Last closing prices:', closing_prices)
            print("- Stop-loss order value:", round(stoploss_orders[symbol], 2), '\n')
        elif any([k > halfprofit_orders[symbol] for k in closing_prices]):
            coverlong_booleans[index] = True
            golong_booleans[index] = True
            print('- Last closing prices:', closing_prices)
            print("- Half-profit order value:", round(halfprofit_orders[symbol], 2), '\n')

    return((coverlong_booleans, golong_booleans))


def go_or_cover_long(eq_symbols, eq_data, eq_supres, portfolio, stoploss_orders, halfprofit_orders, requests_frequency_inmin):
    golong_booleans = [False] * len(eq_symbols)
    coverlong_booleans = [False] * len(eq_symbols)

    for i in range(len(eq_symbols)):
        symbol = eq_symbols[i]
        print('> Checking for ', symbol, '...', sep='')

        # support and resistance values + prices
        (support_value, resistance_value, margin) = eq_supres[i]
        # support_value = eq_supres[i][1] + eq_supres[i][0] * 250.0
        # resistance_value = eq_supres[i][3] + eq_supres[i][2] * 250.0
        # margin = (resistance_value - support_value) / 10
        closing_prices = eq_data[i]['4. close'].values[-requests_frequency_inmin:]

        golong_booleans = is_moment_to_golong(i, symbol, closing_prices, support_value, margin, golong_booleans, portfolio)
        (coverlong_booleans, golong_booleans) = is_moment_to_coverlong(i, symbol, closing_prices, resistance_value, margin, coverlong_booleans, golong_booleans, portfolio, stoploss_orders, halfprofit_orders)

    return((coverlong_booleans, golong_booleans))
