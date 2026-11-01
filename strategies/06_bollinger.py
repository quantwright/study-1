"""Bollinger(20, 2) mean reversion, long only.

Long when the close is below the lower band; exit when the close is above the middle band.
Middle band = SMA(20) of the close; lower band = middle - 2 x the population standard
deviation (divisor n) of the last 20 closes. Orders fill at the next bar's open.
"""
import pandas as pd
from backtesting import Strategy


class BollingerReversion(Strategy):
    period = 20
    width = 2

    def init(self):
        close = pd.Series(self.data.Close)
        mid = close.rolling(self.period).mean()
        lower = mid - self.width * close.rolling(self.period).std(ddof=0)
        self.mid = self.I(lambda: mid.to_numpy(), name='Middle')
        self.lower = self.I(lambda: lower.to_numpy(), name='Lower')

    def next(self):
        close = self.data.Close[-1]
        if not self.position:
            if close < self.lower[-1]:
                self.buy()
        elif close > self.mid[-1]:
            self.position.close()
