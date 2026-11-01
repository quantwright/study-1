"""Time-series momentum 12-1, long only.

At each month's last trading day, be long for the next month if the return from 252 trading days ago
to 21 trading days ago (close[t-21] / close[t-252] - 1) is positive, else flat. Orders fill at the next
bar's open, the first trading day of the next month.
The month's last trading day is found from each bar's own date: the bar is the last weekday (Mon-Fri)
of its month. When that weekday is an exchange holiday (Good Friday or Memorial Day at a month's end)
there is no such bar, and the decision is made on the first bar of the new month instead, one day late.
"""
import pandas as pd
from backtesting import Strategy


class TimeSeriesMomentum(Strategy):
    lookback = 252
    skip = 21

    def init(self):
        days = self.data.index
        month = (days.year * 12 + days.month).to_numpy(dtype=float)
        last_weekday = ((days + pd.offsets.BDay(1)).month != days.month).astype(float)
        close = pd.Series(self.data.Close)
        momentum = (close.shift(self.skip) / close.shift(self.lookback) - 1).to_numpy()
        self.month = self.I(lambda: month, name='Month')
        self.last_weekday = self.I(lambda: last_weekday, name='Last weekday')
        self.momentum = self.I(lambda: momentum, name='Momentum 12-1')
        self.decided_for = 0

    def next(self):
        month = self.month[-1]
        if self.last_weekday[-1] > 0:
            self.decide()
            self.decided_for = month + 1
        elif 0 < self.decided_for < month:
            self.decide()
            self.decided_for = month

    def decide(self):
        if self.momentum[-1] > 0:
            if not self.position:
                self.buy()
        elif self.position:
            self.position.close()
