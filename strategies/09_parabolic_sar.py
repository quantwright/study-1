"""Parabolic SAR(0.02 step, 0.2 max), long only.

Long when price flips above the SAR; exit when it flips below.
Wilder's Parabolic SAR as TA-Lib computes it (TA_SAR): the acceleration factor starts at 0.02,
rises 0.02 with each new extreme point, and is capped at 0.2. The first trend (bar 1) is short when
bar 1's down move (previous low - low) is positive and larger than its up move (high - previous high),
else long. A long flips short when the low touches or crosses the SAR (low <= SAR); a short flips long
when the high touches or crosses it (high >= SAR). On a flip the SAR restarts at the prior extreme point.
Each next SAR = SAR + AF x (EP - SAR), kept beyond the current and previous bar's range (below their
lows while long, above their highs while short). Orders fill at the next bar's open.
"""
import numpy as np
from backtesting import Strategy


def sar_trend(high, low, step, max_step):
    """+1 while the SAR trend is long, -1 while short, after each bar's flip check; NaN on bar 0."""
    high = np.asarray(high, dtype=float)
    low = np.asarray(low, dtype=float)
    trend = np.full(len(high), np.nan)
    if len(high) < 2:
        return trend
    down_move = low[0] - low[1]
    up_move = high[1] - high[0]
    is_long = not (down_move > 0 and down_move > up_move)
    if is_long:
        ep, sar = high[1], low[0]
    else:
        ep, sar = low[1], high[0]
    af = step
    new_high, new_low = high[1], low[1]
    for i in range(1, len(high)):
        prev_high, prev_low = new_high, new_low
        new_high, new_low = high[i], low[i]
        if is_long:
            if new_low <= sar:
                is_long = False
                sar = max(ep, prev_high, new_high)
                af = step
                ep = new_low
                sar = max(sar + af * (ep - sar), prev_high, new_high)
            else:
                if new_high > ep:
                    ep = new_high
                    af = min(af + step, max_step)
                sar = min(sar + af * (ep - sar), prev_low, new_low)
        else:
            if new_high >= sar:
                is_long = True
                sar = min(ep, prev_low, new_low)
                af = step
                ep = new_high
                sar = min(sar + af * (ep - sar), prev_low, new_low)
            else:
                if new_low < ep:
                    ep = new_low
                    af = min(af + step, max_step)
                sar = max(sar + af * (ep - sar), prev_high, new_high)
        trend[i] = 1.0 if is_long else -1.0
    return trend


class ParabolicSar(Strategy):
    step = 0.02
    max_step = 0.2

    def init(self):
        self.trend = self.I(sar_trend, self.data.High, self.data.Low, self.step, self.max_step, name='SAR trend')

    def next(self):
        t = self.trend
        if not self.position:
            if t[-2] < 0 and t[-1] > 0:
                self.buy()
        elif t[-2] > 0 and t[-1] < 0:
            self.position.close()
