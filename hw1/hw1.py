import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da
import datetime as dt
import pandas as pd
import itertools as it
from numpy import *

def generate_prices(start, end, symbols):
    timeofday = dt.timedelta(hours=16)
    timestamps = du.getNYSEdays(start, end, timeofday)
    dataobj = da.DataAccess('Yahoo')
    keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    dataframes = dataobj.get_data(timestamps, symbols, keys)
    data = dict(zip(keys, dataframes))
    return data['close'].values

class Portfolio:
    def __init__(self, prices, symbols, alloc):
        self.prices = prices
        self.symbols = symbols
        self.alloc = alloc
        self.norm_prices = self.prices / self.prices[0, :]
        self.w_norm_prices = self.norm_prices * self.alloc
        self.totals = self.w_norm_prices.sum(axis=1)
        self.returns = self.totals.copy()
        tsu.returnize0(self.returns)
        self.cum_returns = self.totals[-1]
        self.avg_daily_returns = self.returns.mean()
        self.volatility = self.returns.std()
        self.sharpe = sqrt(252) * self.avg_daily_returns / self.volatility
    
    def __str__(self):
        return "Symbols:  %s\nAllocations:  %s\nSharpe Ratio:  %s\nVolatility:  %s\nAverage Daily Return:  %s\nCumulative Return:  %s" % (str(self.symbols), str(self.alloc), str(self.sharpe), str(self.volatility), str(self.avg_daily_returns), str(self.cum_returns))

def optimize(start, end, symbols):
    prices = generate_prices(start, end, symbols)
    possibilities = [p for p in it.product([round(i, 1) for i in arange(0, 1, 0.1)], repeat = len(symbols)) if sum(p) == 1]
    best_pf = None
    for alloc in possibilities:
        temp_pf = Portfolio(prices, symbols, alloc)
        if best_pf == None or temp_pf.sharpe > best_pf.sharpe:
            best_pf = temp_pf
    return best_pf
