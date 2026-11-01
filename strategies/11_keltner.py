"""Keltner breakout, long only.

Middle line EMA(20) of the close; upper band = middle + 2 x ATR(10).
Long when the close is above the upper band; exit when the close is below the middle line.
EMA: alpha = 2 / (n + 1), seeded with the simple mean of the first n values.
True range = max(high - low, |high - previous close|, |low - previous close|), and high - low on
the first bar; ATR(10) is Wilder's: alpha = 1/10, seeded with the mean of the first 10 true ranges.
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


def atr(high, low, close, n):
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    close = np.asarray(close, dtype=float)
    prev_close = np.concatenate(([np.nan], close[:-1]))
    true_range = np.fmax(high - low, np.fmax(np.abs(high - prev_close), np.abs(low - prev_close)))
    return smooth(true_range, n, 1.0 / n)


class KeltnerBreakout(Strategy):
    ema_period = 20
    atr_period = 10
    atr_multiple = 2

    def init(self):
        d = self.data
        mid = smooth(d.Close, self.ema_period, 2.0 / (self.ema_period + 1))
        upper = mid + self.atr_multiple * atr(d.High, d.Low, d.Close, self.atr_period)
        self.mid = self.I(lambda: mid, name='Middle')
        self.upper = self.I(lambda: upper, name='Upper')

    def next(self):
        close = self.data.Close[-1]
        if not self.position:
            if close > self.upper[-1]:
                self.buy()
        elif close < self.mid[-1]:
            self.position.close()
