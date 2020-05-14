########################################################
#################### TIME FUNCTIONS ####################
########################################################

### IMPORTATION ###
from globalenv import *

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

### FUNCTIONS ###
def get_next_trading_hours():
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    one_day = timedelta(days=1)
    holidays_us = holidays.US()

    # Are we in a weekend? Are we in a holiday?
    boolean = True
    if ny_now.weekday() in holidays.WEEKEND:
        print("Today is ", calendar.day_name[ny_now.weekday()], " the ",
        ny_now.day, "th, New York timezone. Markets are closed.", sep="")
    elif ny_now in holidays_us:
        print("Today is a holiday. Markets are closed.")
    else:
        boolean = False
        print("Today is a trading day!")

    if boolean == False:
        op_h = datetime(ny_now.year, ny_now.month, ny_now.day, 9, 30, 00)
        clo_h = datetime(ny_now.year, ny_now.month, ny_now.day, 15, 59, 00)
        nyse_h = (timezone.localize(op_h), timezone.localize(clo_h))
    else:
        # Find next business day
        next_day = ny_now + one_day
        while next_day.weekday() in holidays.WEEKEND or next_day in holidays_us:
            next_day += one_day

        op_h = datetime(next_day.year, next_day.month, next_day.day, 9, 30, 00)
        clo_h = datetime(next_day.year, next_day.month, next_day.day, 15, 59, 00)
        nyse_h = (timezone.localize(op_h), timezone.localize(clo_h))

    return(nyse_h)


def get_requests_frequency(nyse_h, nb_equities):
    diff = (nyse_h[1] - nyse_h[0]).total_seconds() / 60 # nb of trading minutes
    requests_frequency = (diff / (max_nb_requests_per_day / nb_equities)) * 60
    requests_frequency = math.ceil(requests_frequency)
    return(requests_frequency)


def is_market_open(nyse_h):
    boolean = False
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    if ny_now >= nyse_h[0] and ny_now <= nyse_h[1]:
        boolean = True
    return(boolean)


def get_secs_till_op(nyse_h):
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    days_till_op = (nyse_h[0] - ny_now).days * 24 * 60 * 60
    secs_till_op = days_till_op + (nyse_h[0] - ny_now).seconds
    return(secs_till_op)


def is_moment_to_retrieve(nyse_h, requests_frequency):
    boolean = False
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(timezone)
    secs_since_op = (ny_now - nyse_h[0]).seconds
    secs_till_retrieval = requests_frequency - (secs_since_op % requests_frequency)
    if (secs_till_retrieval % 5 == 0.0) and (secs_till_retrieval != requests_frequency):
        print(secs_till_retrieval, "seconds till next retrieval")
    boolean = secs_since_op % requests_frequency == 0.0
    return(boolean)
