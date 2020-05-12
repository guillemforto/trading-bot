########################################################
################### TRADING STRATEGY ###################
########################################################

### IMPORTATION ###
import numpy as np
import sys
import os
# import pattern_detection as patdet
import portfolio_management as pm

### GLOBAL ENV ###


### FUNCTIONS ###
# def setup_is_present():
#     boolean = False
#     if detect_trend(prices, sma_data) == 2:
#         boolean = True
#     return(boolean)


def is_moment_to_golong(index, closing_prices, support_value, margin, golong_booleans):
    """We go long if price close to support (i.e. if price breaches support + margin)"""
    if any([k - margin <= support_value for k in closing_prices]):
        golong_booleans[index] = True
        print("\nTrading opportunity detected! We go long on ", symbol, ".", sep='')
        print('Last closing prices:', closing_prices)
        print("Today's (support + margin) value:", support_value + margin)
    return(golong_booleans)


def is_moment_to_coverlong(index, closing_prices, resistance_value, margin, coverlong_booleans):
    """We cover long if price close to resistance (i.e. if price breaches resistance - margin)"""
    if any([k + margin >= resistance_value for k in closing_prices]):
        coverlong_booleans[index] = True
        print("\nCovering long position for ", symbol, ".", sep='')
        print('Last closing prices:', closing_prices)
        print("Today's (resistance - margin) values:", resistance_value - margin)
    return(coverlong_booleans)


def go_or_cover_long(five_eq_symbols, five_eq_data, five_eq_supres, portfolio, requests_frequency_inmin):
    golong_booleans = [False] * len(five_eq_symbols)
    coverlong_booleans = [False] * len(five_eq_symbols)

    for i in range(len(five_eq_symbols)):
        symbol = five_eq_symbols[i]

        # support and resistance values + prices
        support_value = five_eq_supres[i][1] + five_eq_supres[i][0] * 250.0
        resistance_value = five_eq_supres[i][3] + five_eq_supres[i][2] * 250.0
        margin = (resistance_value - support_value) / 10
        closing_prices = five_eq_data[i]['4. close'].values[-requests_frequency_inmin:]

        if not pm.do_we_currently_own(symbol, portfolio):
            golong_booleans = is_moment_to_golong(i, closing_prices, support_value, margin, golong_booleans)
            coverlong_booleans = is_moment_to_coverlong(i, closing_prices, support_value, margin, coverlong_booleans)

    return((golong_booleans, coverlong_booleans))


# def compute_profit_potential():
#     target_price =
#
#
# def reward_to_loss():
#     risk =
#     if profit_potential > 1.5 * risk:
#         placeOrder
#     return(risk)
