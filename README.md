Research by QuantWright (a commercial backtesting tool). Results came from its API; the code here is plain backtesting.py.

# Study 1: twelve famous strategies on QQQ, one fixed protocol

Twelve textbook strategies, each in one standard form with its standard parameters, tested the same way: QQQ daily, long
only, the product's default costs, March 1999 to December 2024, one version each, all counted. No parameter was tuned.
The protocol was frozen before the first run; [PROTOCOL.md](PROTOCOL.md) is that text, and it lists the SHA-256 of each
file in [`strategies/`](strategies), so you can check that the code here is the code that ran.

## Results, 1999–2024 (QQQ daily, default costs)

| # | Strategy | Trades | Win rate | Max drawdown | Made money after costs | Beat holding QQQ | Grade (score, trials at the time) |
|---|---|---|---|---|---|---|---|
| 01 | RSI(2) 10/90 | 192 | 73% | 72.4% | yes | no | D (49, 1) |
| 02 | RSI(14) 30/70 | 21 | 81% | 77.7% | yes | no | D (35, 2) |
| 03 | MACD 12/26/9 cross | 262 | 45% | 78.2% | yes | no | D (37, 3) |
| 04 | Golden cross 50/200 | 16 | 63% | 28.4% | yes | yes | C (52, 4) |
| 05 | EMA 9/21 cross | 138 | 39% | 45.8% | yes | no | C (62, 5) |
| 06 | Bollinger 20/2 reversion | 110 | 75% | 58.3% | yes | no | D (47, 6) |
| 07 | Donchian / Turtle 20/10 | 111 | 53% | 43.3% | yes | no | D (49, 7) |
| 08 | Supertrend 10/3 | 101 | 50% | 46.0% | yes | no | D (49, 8) |
| 09 | Parabolic SAR 0.02/0.2 | 317 | 47% | 59.9% | yes | no | D (44, 9) |
| 10 | Stochastic 14/3/3 20/80 | 114 | 63% | 74.3% | yes | no | D (35, 10) |
| 11 | Keltner breakout 20/2×ATR10 | 100 | 49% | 35.1% | yes | no | D (49, 11) |
| 12 | Time-series momentum 12-1 | 15 | 80% | 48.3% | yes | no | D (43, 12) |

- All 12 made money after costs, and 11 of 12 did worse than holding QQQ over the same years.
- The golden cross beat holding on 16 trades in 26 years: too few to tell skill from luck.
- A high win rate is not a good result on its own: RSI(2) won 73% of its 192 trades and still had a 72.4% drawdown.
- The grade is the product's, and each is graded against the number of strategies tested up to it (1 to 12). Every grade
  is C or below until a counted held-out test.

## The hold-out, 2 January 2025 – 27 October 2026

Every strategy then ran once, unchanged, on the years after the development window. Four had enough trades to judge
(RSI(2), MACD cross, EMA 9/21 cross, Parabolic SAR), and none of the four beat holding QQQ. The other eight had fewer than
10 trades, so the product withheld their figures, and whether they beat holding is not known.

The product counts only the first held-out test per account and market. The EMA 9/21 cross was that test, chosen by a
rule fixed before the runs: 12 trades, 25% won, grade D (39).

## The tier list

The rule was fixed before the runs (PROTOCOL.md). The tier is not the product's grade.

| Tier | Rule (short) | Strategies |
|---|---|---|
| S | made money and beat holding in both windows, enough trades | none |
| A | made money in both windows, enough trades, didn't beat holding | RSI(2), MACD cross, EMA 9/21 cross, Parabolic SAR |
| B | made money 1999–2024 with enough trades; hold-out too short to judge | Bollinger, Donchian/Turtle, Supertrend, Stochastic, Keltner |
| C | made money 1999–2024, lost on the hold-out | none |
| D | made money, but on fewer than 30 trades in 26 years | RSI(14) 30/70, golden cross, momentum 12-1 |
| F | lost money 1999–2024 | none |

## What is not here

No market data, prices, trade lists, equity curves, buy-and-hold figures or returns: the data's licence doesn't allow
them to be shared. The run ledger is not included for the same reason. Run the files on your own data: your numbers will
differ with your data source, your costs and your account settings.

## Running a strategy on your own data

```bash
pip install -r requirements.txt
```

```python
import importlib.util
import pandas as pd
from backtesting import Backtest

# The file names start with a number, so load a strategy by its path.
spec = importlib.util.spec_from_file_location("rsi2", "strategies/01_rsi2.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Your own daily bars: a DatetimeIndex and Open, High, Low, Close columns (Volume optional).
bars = pd.read_csv("your_qqq_daily.csv", index_col=0, parse_dates=True)
print(Backtest(bars, module.Rsi2, cash=100_000).run())
```

backtesting.py charges no commission by default, and the study ran with the product's default costs (PROTOCOL.md), so
expect different figures.

## Licence

The files in this repository are under the MIT licence ([LICENSE](LICENSE)). backtesting.py is a separate project under
AGPL-3.0; it is not included here, and the strategy files only import it.
