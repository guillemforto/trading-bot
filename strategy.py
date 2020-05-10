########################################################
################### TRADING STRATEGY ###################
########################################################

### IMPORTATION ###
import sys
import os
import pattern_detection as patdet
import portfolio_management as pm

### GLOBAL ENV ###


### FUNCTIONS ###
# def setup_is_present():
#     boolean = False
#     if detect_trend(prices, sma_data) == 2:
#         boolean = True
#     return(boolean)


def is_moment_to_golong(five_eq_symbols, five_eq_data, five_eq_supres):
    """We go long if:
    - we don't already own the stock
    - price close to support (i.e. if price breaches support + margin)"""

    booleans = [False] * 5
    for i in range(len(five_eq_symbols)):
        symbol = five_eq_symbols[i]

        if not pm.do_we_currently_own(symbol, portfolio):
            # support and resistance values
            x_vals = [k for k in range(249, 252)]
            support_values = [five_eq_supres[i][1] + five_eq_supres[i][0] * x for x in x_vals]
            resistance_values = [five_eq_supres[i][3] + five_eq_supres[i][2] * x for x in x_vals]
            margin = (max(resistance_values) - min(support_values)) / 10

            # price
            closing_price = five_eq_data[i]['4. close'].values[-10:]

            if any([any(k - margin <= support_values) for k in closing_price]):
                booleans[i] = True

    return(booleans)


def is_moment_to_coverlong(five_eq_symbols, five_eq_data, five_eq_supres):
    """We go coverlong if:
    - we currently own the stock
    - price close to resistance (i.e. if price breaches resistance - margin)"""

    booleans = [False] * 5
    for i in range(len(five_eq_symbols)):
        symbol = five_eq_symbols[i]

        if pm.do_we_currently_own(symbol, portfolio):
            # support and resistance values
            x_vals = [k for k in range(249, 252)]
            support_values = [five_eq_supres[i][1] + five_eq_supres[i][0] * x for x in x_vals]
            resistance_values = [five_eq_supres[i][3] + five_eq_supres[i][2] * x for x in x_vals]
            margin = (max(resistance_values) - min(support_values)) / 10

            # price
            closing_price = five_eq_data[i]['4. close'].values[-10:]

            # cover long if price close to resistance (i.e. if price breaches resistance - margin)
            if any([any(k + margin >= resistance_values) for k in closing_price]):
                booleans[i] = True

    return(booleans)


# def is_moment_to_goshort():
#     boolean = False
#     resistance_level = 122 # should be a function of price
#     if price > resistance:
#         boolean = True
#     return(boolean)
#
#
# def is_moment_to_covershort():
#     boolean = False
#     support_level = 100
#     if price < support:
#         boolean = True
#     return(boolean)


# def compute_profit_potential():
#     target_price =
#
#
# def reward_to_loss():
#     risk =
#     if profit_potential > 1.5 * risk:
#         placeOrder
#     return(risk)
