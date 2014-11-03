import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import matplotlib
matplotlib.use("Agg")
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep
import argparse

def find_events(symbols, data, b_threshold, m_threshold):
    prices = data['close']
    bol_vals = (prices - pd.rolling_mean(prices, 20))/ pd.rolling_std(prices, 20)
    print "Having a bit of a gander for events..."

    events = copy.deepcopy(bol_vals)
    events *= np.NAN

    timestamps = bol_vals.index

    for symbol in symbols:
        if symbol != 'SPY':
            for i in range(1, len(timestamps)):
                if bol_vals[symbol].ix[timestamps[i-1]] >= b_threshold and bol_vals[symbol].ix[timestamps[i]] <= b_threshold and bol_vals['SPY'].ix[timestamps[i]] >= m_threshold:
                    events[symbol].ix[timestamps[i]] = 1
    return events

def produce_study(start, end, symlist, b_threshold, m_threshold, filename):
    timestamps = du.getNYSEdays(start, end, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    symbols = dataobj.get_symbols_from_list(symlist)
    symbols.append('SPY')

    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataframes = dataobj.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, dataframes))

    for key in keys:
        data[key] = data[key].fillna(method='ffill')
        data[key] = data[key].fillna(method='bfill')
        data[key] = data[key].fillna(1.0)

    events = find_events(symbols, data, b_threshold, m_threshold)

    print "Producing study and saving to %s..." % filename

    ep.eventprofiler(events, data, i_lookback=20, i_lookforward=20, s_filename=filename, b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('bollinger_threshold', type=float)
    argparser.add_argument('market_threshold', type=float)
    argparser.add_argument('filename')
    args = argparser.parse_args()
    produce_study(dt.datetime(2008, 1, 1), dt.datetime(2009, 12, 31), 'sp5002012', args.bollinger_threshold, args.market_threshold, args.filename)
