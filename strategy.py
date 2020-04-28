########################################################
################### TRADING STRATEGY ###################
########################################################

### IMPORTATION ###
import sys
import os

sys.path.append(os.path.abspath("/Users/guillemforto/Desktop/trading_bot/trading_strategy/pattern_detection.py"))
import pattern_detection as patdet

### GLOBAL ENV ###


### FUNCTIONS ###
def setup_is_present():
    boolean = False
    MA_threshold = 200
    if price > MA_threshold:
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


def is_moment_to_goshort():
    boolean = False
    resistance_level = 122 # should be a function of price
    if price > resistance:
        boolean = True
    return(boolean)


def is_moment_to_covershort():
    boolean = False
    support_level = 100
    if price < support:
        boolean = True
    return(boolean)


def compute_profit_potential():
    target_price =


def reward_to_loss():
    risk =
    if profit_potential > 1.5 * risk:
        placeOrder
    return(risk)
