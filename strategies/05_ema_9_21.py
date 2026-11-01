"""EMA 9/21 cross, long only.

Long when EMA(9) of the close crosses above EMA(21); exit when it crosses below.
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


class EmaCross(Strategy):
    fast_period = 9
    slow_period = 21

    def init(self):
        self.fast = self.I(ema, self.data.Close, self.fast_period, name='EMA9')
        self.slow = self.I(ema, self.data.Close, self.slow_period, name='EMA21')

    def next(self):
        f, s = self.fast, self.slow
        if not self.position:
            if f[-2] <= s[-2] and f[-1] > s[-1]:
                self.buy()
        elif f[-2] >= s[-2] and f[-1] < s[-1]:
            self.position.close()
