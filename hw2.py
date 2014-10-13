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

def find_events(symbols, data, threshold):
    actual_close = data['actual_close']
    
    print "Having a bit of a gander for events..."

    events = copy.deepcopy(actual_close)
    events *= np.NAN

    timestamps = actual_close.index

    for symbol in symbols:
        for i in range(1, len(timestamps)):
            if actual_close[symbol].ix[timestamps[i-1]] >= threshold and actual_close[symbol].ix[timestamps[i]] < threshold:
                events[symbol].ix[timestamps[i]] = 1
    return events

def produce_study(start, end, symlist, threshold, filename):
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

    events = find_events(symbols, data, threshold)

    print "Producing study and saving to %s..." % filename

    ep.eventprofiler(events, data, i_lookback=20, i_lookforward=20, s_filename=filename, b_market_neutral=True, b_errorbars=True, s_market_sym='SPY')
