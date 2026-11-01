"""RSI(14) 30/70, long only.

Long when RSI(14) closes below 30; exit when RSI(14) closes above 70.
RSI is Wilder's: the average gain and the average loss are smoothed with alpha = 1/n,
each seeded with the simple mean of the first n changes; RSI = 100 - 100 / (1 + gain / loss),
and 100 when the average loss is 0. Orders fill at the next bar's open.
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


def rsi(close, n):
    change = np.diff(np.asarray(close, dtype=float), prepend=np.nan)
    gain = smooth(np.clip(change, 0, None), n, 1.0 / n)
    loss = smooth(np.clip(-change, 0, None), n, 1.0 / n)
    return np.where(loss == 0, 100.0, 100.0 - 100.0 / (1.0 + gain / loss))


class Rsi14(Strategy):
    rsi_period = 14
    entry_below = 30
    exit_above = 70

    def init(self):
        self.rsi = self.I(rsi, self.data.Close, self.rsi_period, name='RSI')

    def next(self):
        if not self.position:
            if self.rsi[-1] < self.entry_below:
                self.buy()
        elif self.rsi[-1] > self.exit_above:
            self.position.close()
