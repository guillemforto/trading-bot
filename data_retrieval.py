########################################################
############### DATA RETRIEVAL FUNCTIONS ###############
########################################################

### IMPORTATION ###
import globalenv
from globalenv import *
import supres as supres


### FUNCTIONS ###
def get_PERatio(symbol):
    url = 'https://finance.yahoo.com/quote/' + symbol + '?p=' + symbol + '&.tsrc=fin-srch'
    table = pd.read_html(requests.get(url).content)[1]
    PER_ttm = np.float(table.loc[table[0] == 'PE Ratio (TTM)'][1].values[0])
    if math.isnan(PER_ttm):
        PER_ttm = None
    return(PER_ttm)


def get_equities_table():
    PERatio = []
    print("Getting PE Ratios...")
    for symbol in tqdm.tqdm(globalenv.real_time_tickers):
        PERatio.append(get_PERatio(symbol))
        time.sleep(0.5)

    equities_table = pd.DataFrame(globalenv.real_time_tickers.items(), columns=['Symbol', 'Name'])
    equities_table['PE Ratio (TTM)'] = PERatio
    print('Done!')
    return(equities_table)


def get_candidate_equities():
    table = get_equities_table()

    # Low PER: Q1 < PE ratio (TTM) < Q2
    table = table[~table['PE Ratio (TTM)'].isna()]
    per_q1 = table['PE Ratio (TTM)'].quantile(0.25)
    per_q2 = table['PE Ratio (TTM)'].quantile(0.5)
    q1q2 = table[table['PE Ratio (TTM)'] >= per_q1]
    q1q2 = q1q2[q1q2['PE Ratio (TTM)'] <= per_q2]

    if len(q1q2) > 10:
        candidates_table = q1q2
    else:
        candidates_table = table

    candidates_table = table
    # tmp = candidates_table['% Change'].apply(lambda x: float(x[:-1])).values
    # candidates_table = candidates_table.drop(['% Change'], axis = 1)
    # candidates_table['% Change'] = tmp
    #
    # candidates_table.sort_values(by="% Change", ascending=False, inplace=True)

    candidates_table.reset_index(inplace=True, drop=True)
    return(candidates_table)


def select_top_gainer(candidates_table):
    top_gainer = candidates_table['Symbol'][0]
    top_gainer_name = candidates_table['Name'][0]
    candidates_table.drop(index=0, inplace=True)
    candidates_table.reset_index(inplace=True, drop=True)
    return((top_gainer, top_gainer_name, candidates_table))


def get_1_equity_data(symbol):
    print("Trying to get/update data for", symbol)
    data, meta_data = globalenv.ts.get_intraday(symbol=symbol, interval='1min', outputsize='compact')
    data.sort_index(inplace=True)
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(globalenv.timezone)
    # data = data[data.index.day == 8] # subset to intraday prices
    data = data[data.index.day == ny_now.day] # subset to intraday prices
    return(data)

# data, meta_data = ts.get_intraday(symbol="CBL", interval='1min', outputsize='compact')
# data

def is_data_available(data):
    boolean = True
    ny_now = pytz.utc.localize(datetime.utcnow()).astimezone(globalenv.timezone)
    if data.empty:
        boolean = False
    else:
        set_of_days = list(data[~data.index.day.duplicated()].index.day)
        if (ny_now.day not in set_of_days): # (8 not in set_of_days)
            boolean = False
    return(boolean)


def is_there_appropriate_supres(symbol):
    boolean = False
    h = supres.get_hist_data(symbol)
    (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(h, window=len(h), errpct=0.01, sortError=False, accuracy=1)
    try:
        (best_sup, best_res) = supres.filter_best_supres(mintrend, maxtrend, h)
        supres.plot_supres(h, minimaIdxs, maximaIdxs, best_sup, best_res, symbol)
        print("Is it okay to keep", symbol, '?')
        x = input("[y/n]: ")
        # x = 'y'
        if x == 'y' or x == 'Y':
            boolean = True
    except:
        print("No suitable support / resistance found for", symbol)

    return(boolean)


def get_supres(symbol):
    h = supres.get_hist_data(symbol)
    (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(h, window=len(h), errpct=0.01, sortError=False, accuracy=1)
    (best_sup, best_res) = supres.filter_best_supres(mintrend, maxtrend, h)
    support_value = best_sup[1][1] + best_sup[1][0] * len(h)
    resistance_value = best_res[1][1] + best_res[1][0] * len(h)
    margin = (resistance_value - support_value) / 10
    return((support_value, resistance_value, margin))


def get_5_equities_data(candidates_table):
    eq_symbols = []
    eq_data = []
    while len(eq_symbols) < 5:
        if len(candidates_table) == 0:
            print('\nNo stocks left in the candidates table.')
            break
        else:
            print('\n> ', len(candidates_table), ' stocks left in the candidates table.', sep='')

        (top_gainer, top_gainer_name, candidates_table) = select_top_gainer(candidates_table)
        print("\nSymbol:", top_gainer, '-', top_gainer_name)

        bool1 = is_there_appropriate_supres(top_gainer)
        if not bool1:
            time.sleep(1)
            continue
        else:
            try:
                data = get_1_equity_data(top_gainer)
            except:
                data = pd.DataFrame({})
            bool2 = is_data_available(data)
            if not bool2:
                print("No intraday data available for ", top_gainer, sep="")
                time.sleep(10)
                continue
            else:
                print('Intraday data is available for ', top_gainer, '!', sep='')
                eq_symbols.append(top_gainer)
                eq_data.append(data)
                print('\nTicker added to the list:', eq_symbols)

    # Getting support and resistances
    eq_supres = []
    for symbol in eq_symbols:
        eq_supres.append(get_supres(symbol))

    print('The final list is:', eq_symbols, '\n')

    print('Done!')
    return((eq_symbols, eq_data, eq_supres))



def update_5_equities_data(eq_symbols):
    print("\nUpdating data for our equities:")
    eq_data = []
    for symbol in eq_symbols:
        eq_data.append(get_1_equity_data(symbol))
    print("Done!\n")
    return(eq_data)
