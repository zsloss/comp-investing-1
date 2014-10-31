import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import pandas as pd
import argparse

def generate_prices(start, end, symbols):
    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(start, end, timeofday)
    dataobj = da.DataAccess('Yahoo')
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataframes = dataobj.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, dataframes))
    return data['close']

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('year', type=int)
    argparser.add_argument('month', type=int)
    argparser.add_argument('day', type=int)
    argparser.add_argument('symbol')
    args = argparser.parse_args()
    prices = generate_prices(dt.datetime(2010, 1, 1), dt.datetime(2010, 12, 31), [args.symbol])
    print ((prices - pd.rolling_mean(prices, 20))/ pd.rolling_std(prices, 20)).ix[dt.datetime(args.year, args.month, args.day, 16)]
