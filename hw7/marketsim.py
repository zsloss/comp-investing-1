import argparse
import csv
import pandas as pd
import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import numpy as np

def read_orders(filename):
    reader = csv.reader(open(filename, 'rU'), delimiter=',')
    orders = []
    for row in reader:
        orders.append([dt.datetime(int(row[0]), int(row[1]), int(row[2])), row[3], row[4], row[5]])
    return pd.DataFrame(data=orders, columns=['Date', 'Symbol', 'Buy/Sell', 'Quantity'])

def generate_prices(start, end, symbols):
    timestamps = du.getNYSEdays(start, end, dt.timedelta(hours=16))
    dataobj = da.DataAccess('Yahoo')
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataframes = dataobj.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, dataframes))
    return data['close']

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('initial_cash', type=float)
    argparser.add_argument('input_csv')
    args = argparser.parse_args()
    orders = read_orders(args.input_csv)
    symbols = list(set(orders['Symbol']))
    start_date = orders.iloc[0]['Date']
    end_date = orders.iloc[-1]['Date']
    prices = generate_prices(start_date, end_date + dt.timedelta(days=1), symbols)
    prices = prices.fillna(method='ffill')
    prices = prices.fillna(method='bfill')
    prices = prices.fillna(1.0)
    timeofday = dt.timedelta(hours=16)
    timestamps = pd.date_range(start=start_date, end=end_date)
    timestamps = du.getNYSEdays(start_date, end_date + dt.timedelta(days=1), timeofday)
    portfolio = pd.DataFrame(index=timestamps, columns=(symbols + ['Cash', 'Value']))
    portfolio.fillna(value=0.0, inplace=True)

    for i in range(len(orders)):
        if orders.iloc[i]['Buy/Sell'].lower() == 'buy':
            buy_or_sell = 1
        elif orders.iloc[i]['Buy/Sell'].lower() == 'sell':
            buy_or_sell = -1
        date = orders.iloc[i]['Date'] + timeofday
        quantity = int(orders.iloc[i]['Quantity'])
        portfolio.loc[date][orders.iloc[i]['Symbol']] += quantity * buy_or_sell
        portfolio.loc[date]['Cash'] += buy_or_sell * -1 * quantity * prices.loc[date][orders.iloc[i]['Symbol']] 

    for i in range(0, len(portfolio)):
        row = portfolio.iloc[i]
        if i == 0:
            row['Cash'] += args.initial_cash
        else:
            portfolio.iloc[i] += portfolio.iloc[i-1]
        value = 0
        for symbol in symbols:
            value += row[symbol] * prices.loc[portfolio.index[i]][symbol]
        value += row['Cash']
        row['Value'] = value

    print portfolio
    print "Return: %s" % (portfolio['Value'][-1] / portfolio['Value'][0])
    daily_returns = portfolio['Value'].copy()
    tsu.returnize0(daily_returns)
    volatility = daily_returns.std()
    print "Volatility: %s" % (volatility)
    avg_daily_return = daily_returns.mean()
    print "Average Daily Return: %s" % (avg_daily_return)
    print "Sharpe Ratio: %s" % (avg_daily_return * np.sqrt(252) / volatility)

