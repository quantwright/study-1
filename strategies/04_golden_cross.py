"""Golden cross 50/200, long only.

Long when SMA(50) of the close crosses above SMA(200); exit when it crosses below.
A crosses above B on a bar when A > B on that bar and A <= B on the bar before (below: the mirror).
Orders fill at the next bar's open.
"""
import pandas as pd
from backtesting import Strategy


def sma(values, n):
    return pd.Series(values).rolling(n).mean().to_numpy()


class GoldenCross(Strategy):
    fast_period = 50
    slow_period = 200

    def init(self):
        self.fast = self.I(sma, self.data.Close, self.fast_period, name='SMA50')
        self.slow = self.I(sma, self.data.Close, self.slow_period, name='SMA200')

    def next(self):
        f, s = self.fast, self.slow
        if not self.position:
            if f[-2] <= s[-2] and f[-1] > s[-1]:
                self.buy()
        elif f[-2] >= s[-2] and f[-1] < s[-1]:
            self.position.close()
