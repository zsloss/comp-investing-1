import argparse
import csv
import pandas as pd
import numpy as np
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
from operator import itemgetter

def find_events(symbols, data, e_threshold, m_threshold):
    
    print "Finding events..."

    timestamps = data.index
    events = []
    for symbol in symbols:
        for i in range(1, len(timestamps)):
            if data[symbol].ix[timestamps[i-1]] >= e_threshold and data[symbol].ix[timestamps[i]] <= e_threshold and data['SPY'].ix[timestamps[i]] >= m_threshold:
                buy_date = timestamps[i]
                events.append([buy_date.year, buy_date.month, buy_date.day, symbol, 'BUY', 100])
                if i + 5 < len(timestamps):
                    sell_date = timestamps[i + 5]
                else:
                    sell_date = timestamps[-1]
                events.append([sell_date.year, sell_date.month, sell_date.day, symbol, 'SELL', 100])
    return events

def write_csv(lst, filename):
    with open(filename, 'wb') as f:
        writer = csv.writer(f)
        for e in lst:
            writer.writerow(e)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('equity_threshold', type=float)
    argparser.add_argument('market_threshold', type=float)
    argparser.add_argument('output_csv')
    args = argparser.parse_args()
    start = dt.datetime(2008, 1, 1)
    end = dt.datetime(2009, 12, 31)

    timestamps = du.getNYSEdays(start, end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    symbols = dataobj.get_symbols_from_list('sp5002012')
    symbols.append('SPY')
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataframes = dataobj.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, dataframes))

    prices = data['close']
    bol_vals = (prices - pd.rolling_mean(prices, 20))/ pd.rolling_std(prices, 20)

    events = find_events(symbols, bol_vals, args.equity_threshold, args.market_threshold)

    write_csv(sorted(events, key=itemgetter(0, 1, 2)), args.output_csv)
