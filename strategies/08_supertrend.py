"""Supertrend(10, 3), long only.

Long when Supertrend flips to up; exit when it flips to down.
True range = max(high - low, |high - previous close|, |low - previous close|), and high - low on
the first bar. ATR(10) is Wilder's: alpha = 1/10, seeded with the mean of the first 10 true ranges.
Basic bands: (high + low) / 2 +/- 3 x ATR. Final upper band: the basic upper band if it is below the
previous final upper band or the previous close was above it, else the previous final upper band;
final lower band: the mirror. The trend starts down on the first bar with an ATR. While down it turns
up when the close is above the final upper band; while up it turns down when the close is below the
final lower band. Orders fill at the next bar's open.
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


def supertrend_direction(high, low, close, n, mult):
    """+1 while the trend is up, -1 while it is down, NaN before the first ATR."""
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    close = np.asarray(close, dtype=float)
    prev_close = np.concatenate(([np.nan], close[:-1]))
    true_range = np.fmax(high - low, np.fmax(np.abs(high - prev_close), np.abs(low - prev_close)))
    atr = smooth(true_range, n, 1.0 / n)
    upper = (high + low) / 2 + mult * atr
    lower = (high + low) / 2 - mult * atr
    direction = np.full(len(close), np.nan)
    start = int(np.argmax(~np.isnan(atr)))
    if np.isnan(atr[start]):
        return direction
    direction[start] = -1.0
    for i in range(start + 1, len(close)):
        if not (upper[i] < upper[i - 1] or close[i - 1] > upper[i - 1]):
            upper[i] = upper[i - 1]
        if not (lower[i] > lower[i - 1] or close[i - 1] < lower[i - 1]):
            lower[i] = lower[i - 1]
        if direction[i - 1] < 0:
            direction[i] = 1.0 if close[i] > upper[i] else -1.0
        else:
            direction[i] = -1.0 if close[i] < lower[i] else 1.0
    return direction


class Supertrend(Strategy):
    atr_period = 10
    multiplier = 3

    def init(self):
        self.direction = self.I(supertrend_direction, self.data.High, self.data.Low, self.data.Close,
                                self.atr_period, self.multiplier, name='Direction')

    def next(self):
        d = self.direction
        if not self.position:
            if d[-2] < 0 and d[-1] > 0:
                self.buy()
        elif d[-2] > 0 and d[-1] < 0:
            self.position.close()
