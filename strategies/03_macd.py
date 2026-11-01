"""MACD(12, 26, 9) cross, long only.

Long when the MACD line crosses above the signal line; exit when it crosses below.
MACD line = EMA(12) - EMA(26) of the close; signal line = EMA(9) of the MACD line.
EMA: alpha = 2 / (n + 1), seeded with the simple mean of the first n values.
A crosses above B on a bar when A > B on that bar and A <= B on the bar before (below: the mirror).
Orders fill at the next bar's open.
"""
import numpy as np
from backtesting import Strategy


def smooth(values, n, alpha):
    """out[i] = alpha * x[i] + (1 - alpha) * out[i-1], seeded with the mean of the first n values (leading NaNs skipped)."""
    x = np.asarray(values, dtype=float)
    out = np.full(len(x), np.nan)
    first = int(np.argmax(~np.isnan(x)))
    seed = first + n - 1
    if seed >= len(x):
        return out
    out[seed] = x[first:seed + 1].mean()
    for i in range(seed + 1, len(x)):
        out[i] = alpha * x[i] + (1 - alpha) * out[i - 1]
    return out


def ema(values, n):
    return smooth(values, n, 2.0 / (n + 1))


class MacdCross(Strategy):
    fast_period = 12
    slow_period = 26
    signal_period = 9

    def init(self):
        self.macd = self.I(lambda c: ema(c, self.fast_period) - ema(c, self.slow_period), self.data.Close, name='MACD')
        self.signal = self.I(lambda m: ema(m, self.signal_period), self.macd, name='Signal')

    def next(self):
        m, s = self.macd, self.signal
        if not self.position:
            if m[-2] <= s[-2] and m[-1] > s[-1]:
                self.buy()
        elif m[-2] >= s[-2] and m[-1] < s[-1]:
            self.position.close()
