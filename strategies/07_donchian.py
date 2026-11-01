"""Donchian / Turtle System 1 breakout, long only (the stated close rule only).

Long when the close is above the highest high of the previous 20 bars; exit when the close
is below the lowest low of the previous 10 bars. "Previous" leaves the current bar out.
Orders fill at the next bar's open.
"""
import pandas as pd
from backtesting import Strategy


class DonchianBreakout(Strategy):
    entry_period = 20
    exit_period = 10

    def init(self):
        self.prior_high = self.I(lambda h: pd.Series(h).rolling(self.entry_period).max().shift(1).to_numpy(), self.data.High, name='High20')
        self.prior_low = self.I(lambda low: pd.Series(low).rolling(self.exit_period).min().shift(1).to_numpy(), self.data.Low, name='Low10')

    def next(self):
        close = self.data.Close[-1]
        if not self.position:
            if close > self.prior_high[-1]:
                self.buy()
        elif close < self.prior_low[-1]:
            self.position.close()
