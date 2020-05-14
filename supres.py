########################################################
################## SUPRES DETECTION ####################
########################################################

### IMPORTATION ###
from globalenv import *


### FUNCTIONS ###
def get_hist_data(ticker):
    tick = yf.Ticker(ticker)
    hist = tick.history(period="max", rounding=True)
    hist = hist[-250:]
    h = hist.Close.tolist()
    return(h)


def keep_halfLasting_supres(mintrend, maxtrend, h, lengthThreshold=40):
    """Only keep the support and resistances which last for at least more than lengthThreshold% of the prices"""
    longest_mintrends = [i for i in range(len(mintrend)) if (mintrend[i][0][-1] - mintrend[i][0][0])/len(h)*100 >= lengthThreshold]
    longest_maxtrends = [j for j in range(len(maxtrend)) if (maxtrend[j][0][-1] - maxtrend[j][0][0])/len(h)*100 >= lengthThreshold]
    candidates = [(i,j) for i in longest_mintrends for j in longest_maxtrends]

    return(candidates)


def keep_parallel_supres(mintrend, maxtrend, h):
    """Only keep the support and resistances that never cross between [len(h) +- 30%]"""
    candidates = []
    margin = int(len(h)/100*30)

    for i in range(len(mintrend)):
        intercept_min = mintrend[i][1][1]
        slope_min = mintrend[i][1][0]
        y_min = [intercept_min + slope_min * k for k in range(- margin, len(h) + margin)]

        for j in range(len(maxtrend)):
            intercept_max = maxtrend[j][1][1]
            slope_max = maxtrend[j][1][0]
            y_max = [intercept_max + slope_max * k for k in range(- margin, len(h) + margin)]

            if all([y_min[i] < y_max[i] for i in range(len(y_min))]):
                candidates.append((i,j))

    return(candidates)


def keep_similarPeriod_supres(mintrend, maxtrend):
    """Only keep the support and resistances which have at least commpct% of their length in common"""
    candidates = []
    for i in range(len(mintrend)):
        supp = [k for k in range(mintrend[i][0][0], mintrend[i][0][-1] + 1)]
        for j in range(len(maxtrend)):
            res = [k for k in range(maxtrend[j][0][0], maxtrend[j][0][-1] + 1)]
            inter = list(set(supp) & set(res))
            if inter != [] and (len(inter) >= (len(supp)/2) or len(inter) >= (len(res)/2)):
                candidates.append((i,j))

    return(candidates)


def keep_recent_supres(mintrend, maxtrend, h, pct_threshold=70):
    """Only keep the support and resistances whose last point is in the last pct_threshold%"""
    candidates = []
    last_third = len(h) / 100 * pct_threshold
    for i in range(len(mintrend)):
        for j in range(len(maxtrend)):
            if mintrend[i][0][-1] >= last_third and maxtrend[j][0][-1] >= last_third:
                candidates.append((i,j))

    return(candidates)


def keep_lastPriceContained_supres(mintrend, maxtrend, h):
    candidates = []
    last_price = h[-1]
    for i in range(len(mintrend)):
        last_sup_val = mintrend[i][1][1] + len(h) * mintrend[i][1][0]
        for j in range(len(maxtrend)):
            last_res_val = maxtrend[j][1][1] + len(h) * maxtrend[j][1][0]
            if last_price > last_sup_val and last_price < last_res_val:
                candidates.append((i,j))
    return(candidates)


def keep_lowerRiemann_supres(best_candidates, mintrend, maxtrend):
    if best_candidates != []:
        l = [i[0] + i[1] for i in best_candidates]
        a = l.index(min(l))
        return((mintrend[best_candidates[a][0]], maxtrend[best_candidates[a][1]]))


def filter_best_supres(mintrend, maxtrend, h):
    mintrend, maxtrend = mintrend[:10], maxtrend[:10]
    candidates0 = keep_halfLasting_supres(mintrend, maxtrend, h, lengthThreshold=35)
    candidates1 = keep_parallel_supres(mintrend, maxtrend, h)
    candidates2 = keep_similarPeriod_supres(mintrend, maxtrend)
    candidates3 = keep_recent_supres(mintrend, maxtrend, h, pct_threshold=65)
    candidates4 = keep_lastPriceContained_supres(mintrend, maxtrend, h)
    best_candidates = list(set(candidates0) & set(candidates1) & set(candidates2) & set(candidates3) & set(candidates4))
    (best_sup, best_res) = keep_lowerRiemann_supres(best_candidates, mintrend, maxtrend)
    return((best_sup, best_res))


def abline(x_vals, slope, intercept):
    """Plot a line from slope and intercept"""
    y_vals = [intercept + slope * i for i in x_vals]
    plt.plot(x_vals, y_vals, '--')


def plot_supres(h, minimaIdxs, maximaIdxs, best_sup, best_res, symbol):
    figure(num=None, figsize=(10, 8), dpi=80, facecolor='w', edgecolor='k')
    plt.plot(h, color="black")

    # dots
    mins = [h[i] for i in minimaIdxs]
    maxs = [h[i] for i in maximaIdxs]
    plt.plot(minimaIdxs, mins, linestyle='', marker='o', color='chartreuse')
    plt.plot(maximaIdxs, maxs, linestyle='', marker='o', color='b')

    # graph
    plt.title(symbol + ' price evolution - last year')
    plt.axvline(0, color='purple')
    plt.axhline(0, color='purple')

    # trendlines
    margin = int(len(h)/100*30)
    x1 = best_sup[0]
    x1.append(len(h) + margin)
    x1.insert(0, - margin)
    x2 = best_res[0]
    x2.append(len(h) + margin)
    x2.insert(0, - margin)
    abline(x1, best_sup[1][0], best_sup[1][1])
    abline(x2, best_res[1][0], best_res[1][1])
    plt.show()


# ticker = 'OLLI'
# h = get_hist_data(ticker)
# (minimaIdxs, pmin, mintrend, minwindows), (maximaIdxs, pmax, maxtrend, maxwindows) = trendln.calc_support_resistance(h, window=len(h), errpct=0.01, sortError=False, accuracy=1)
# (best_sup, best_res) = filter_best_supres(mintrend, maxtrend, h)
# plot_supres(h, minimaIdxs, maximaIdxs, best_sup, best_res, ticker)
