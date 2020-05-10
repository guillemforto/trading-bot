########################################################
################### TRADING STRATEGY ###################
########################################################

### IMPORTATION ###
import sys
import os
import pattern_detection as patdet

### GLOBAL ENV ###


### FUNCTIONS ###
def setup_is_present():
    boolean = False
    if detect_trend(prices, sma_data) == 2:
        boolean = True
    return(boolean)


def is_moment_to_golong():
    boolean = False
    resistance_level = 122 # should be a function of price
    if price > resistance:
        boolean = True
    return(boolean)


def is_moment_to_coverlong():
    boolean = False
    support_level = 100
    if price < support:
        boolean = True
    return(boolean)


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


def compute_profit_potential():
    target_price =


def reward_to_loss():
    risk =
    if profit_potential > 1.5 * risk:
        placeOrder
    return(risk)
