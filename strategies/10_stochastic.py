"""Stochastic(14, 3, 3) 20/80, long only.

Long when the slow %K crosses above 20 from below; exit when it crosses below 80 from above.
Fast %K = 100 x (close - lowest low of 14 bars) / (highest high of 14 bars - lowest low of 14 bars),
the current bar included; slow %K = SMA(3) of fast %K. (The second 3, the slow %D, is not used by the rule.)
Crosses above 20: slow %K > 20 on the bar and <= 20 on the bar before; crosses below 80: slow %K < 80
on the bar and >= 80 on the bar before. Orders fill at the next bar's open.
"""
import pandas as pd
from backtesting import Strategy


def slow_k(high, low, close, n, smoothing):
    highest = pd.Series(high).rolling(n).max()
    lowest = pd.Series(low).rolling(n).min()
    fast = 100 * (pd.Series(close) - lowest) / (highest - lowest)
    return fast.rolling(smoothing).mean().to_numpy()


class Stochastic(Strategy):
    k_period = 14
    k_smoothing = 3
    entry_level = 20
    exit_level = 80

    def init(self):
        self.k = self.I(slow_k, self.data.High, self.data.Low, self.data.Close, self.k_period, self.k_smoothing, name='Slow %K')

    def next(self):
        k = self.k
        if not self.position:
            if k[-2] <= self.entry_level and k[-1] > self.entry_level:
                self.buy()
        elif k[-2] >= self.exit_level and k[-1] < self.exit_level:
            self.position.close()
