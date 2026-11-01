# Study 1, wave 1: twelve famous strategies on QQQ, one fixed protocol

**Frozen before any run, 2026-10-28.** The strategy files are fixed by the SHA-256 hashes at the bottom of this page. Nothing below changes after the first run. A change would be a new study with a new protocol.

## What is tested

Twelve textbook strategies, each in one standard form with its standard parameters. No parameter is tuned, and every strategy runs once on the development window. The product's held-out test runs each one once on the hold-out, in an order chosen and recorded after the development runs.

## The fixed protocol

- **Product and contract.** QuantWright Agent API (MCP, https://quantwright.com/api/mcp), code contract as of 28 Oct 2026. The full text is saved in `describe_data.json`. Each strategy is one backtesting.py `Strategy` class, run in the product's sandbox.
- **Market.** QQQ, daily bars (`symbol: "QQQ"`, `timeframe: "1d"`). The product describes its daily US stock and ETF data as *"split-adjusted, as total returns (cash dividends credited on each ex-date)"*. Prices are split-adjusted, not dividend-adjusted. A position held into an ex-date is credited the dividend in cash. All indicators are computed on these split-adjusted prices.
- **Development window.** Asked as `{"from": "1999-03-10", "to": "2024-12-31"}`. describe_data does not state QQQ's first daily bar. If the data starts later, each result's `window.start_later.first_bar` names the first bar, and the run uses it.
- **Hold-out.** From 2025-01-01 to the latest bar. It is set once, in `create_study`, and only `run_held_out_test` reads it. The product counts only the first held-out test per account and market; later ones run and are labelled as not the one that counts. The order of the twelve held-out tests is chosen after the development runs and recorded with the results. A held-out run with fewer than 10 trades has its figures withheld by the product (trade floor), and each development run's `hold_out_estimate` predicts that count.
- **Every window starts flat.** On the development window there are no earlier bars, so each indicator warms up inside the window: a strategy cannot trade until its indicators exist. The golden cross needs 200 bars and momentum 12-1 needs 253. On the hold-out, the product first runs earlier bars so the indicators have history (`window.warmup`), but it places no order on them and the account enters the window flat. A strategy whose entry is a cross, flip or month-end decision that happened before the window waits for its next entry signal inside the window.
- **Signals and fills.** Each decision is made at a bar's close (backtesting.py `next()`, which sees only bars up to the current one). The order fills at the **next bar's open**, for entries and exits alike. The contract says: *"self.buy(), self.sell() and self.position.close() fill at the OPEN of the bar after the one whose next() placed them"*. A position still open at the end of a window is closed on its last bar (the trade list says "open at the end").
- **Costs.** The product's defaults. No `costs` argument is sent. The contract describes costs as *"the commission charged once per round trip on the value at entry, the slippage on each fill"*. The default for US stocks and ETFs on daily bars is a 0.5 bp commission (0.00005) and 1 bp slippage per fill (0.0001), the product's published defaults. Both are debited from cash at the fill, and fills are at the raw next-bar open. The record is each result's `settings.commission` and `settings.slippage`, which the ledger keeps per run.
- **Account and sizing.** The product's default account, US$100,000 (`account_usd` not sent), with no leverage. Every strategy enters with a bare `self.buy()`, the same for all twelve. That is backtesting.py's default size, all of the equity: as many whole shares as the cash buys at the fill price. The contract also allows `size=0.99`; the default is used instead.
- **Long only, one position.** A strategy enters only when flat and exits only when long. There is no shorting, no pyramiding (`max_entries_per_side` is not set) and no leverage.
- **No additions.** No stop, target, filter or time limit is added to any rule.
- **Settings in the code.** Every rule number (periods, levels, multipliers) is a class-level setting, as the contract requires, at the standard value given below.
- **Crossing.** A crosses above B on a bar when A > B on that bar and A <= B on the bar before; crossing below is the mirror. This is checked on closed bars only. Levels work the same way (for example, %K crossing above 20).
- **No look-ahead.** No negative shift, and no read of any bar after the current one. Every indicator is computed from the current and earlier bars only. Local tests confirm it by cutting the data short (see "Local verification").

## The twelve definitions

| # | File | Strategy | Rule as implemented |
|---|---|---|---|
| 1 | `01_rsi2.py` | RSI(2) 10/90 | Long when RSI(2) closes below 10; exit when RSI(2) closes above 90. |
| 2 | `02_rsi14.py` | RSI(14) 30/70 | Long when RSI(14) closes below 30; exit when RSI(14) closes above 70. |
| 3 | `03_macd.py` | MACD(12, 26, 9) cross | Long when the MACD line crosses above the signal line; exit when it crosses below. |
| 4 | `04_golden_cross.py` | Golden cross 50/200 | Long when SMA(50) crosses above SMA(200); exit when it crosses below. |
| 5 | `05_ema_9_21.py` | EMA 9/21 cross | Long when EMA(9) crosses above EMA(21); exit when it crosses below. |
| 6 | `06_bollinger.py` | Bollinger(20, 2) mean reversion | Long when the close is below the lower band; exit when the close is above the middle band. |
| 7 | `07_donchian.py` | Donchian / Turtle System 1 | Long when the close is above the highest high of the previous 20 bars; exit when the close is below the lowest low of the previous 10 bars. |
| 8 | `08_supertrend.py` | Supertrend(10, 3) | Long when Supertrend flips to up; exit when it flips to down. |
| 9 | `09_parabolic_sar.py` | Parabolic SAR(0.02, 0.2) | Long when the SAR flips below price (trend to long); exit when it flips above price. |
| 10 | `10_stochastic.py` | Stochastic(14, 3, 3) 20/80 | Long when slow %K crosses above 20 from below; exit when it crosses below 80 from above. |
| 11 | `11_keltner.py` | Keltner breakout | Long when the close is above EMA(20) + 2 × ATR(10); exit when the close is below EMA(20). |
| 12 | `12_tsmom_12_1.py` | Time-series momentum 12-1 | On each month's last trading day, long for the next month if close[t−21] / close[t−252] − 1 > 0, else flat. |

## Indicator formulas

- **SMA(n):** the mean of the last n closes, the current one included.
- **EMA(n):** out[t] = α·x[t] + (1 − α)·out[t−1], with α = 2/(n+1). It is seeded on the n-th valid value with the simple mean of the first n values, and is undefined before that.
- **Wilder smoothing (RMA(n)):** the same recursion with α = 1/n, which is avg[t] = (avg[t−1]·(n−1) + x[t]) / n, seeded with the simple mean of the first n values.
- **RSI(n), Wilder:** change[t] = close[t] − close[t−1]. Gain = max(change, 0) and loss = max(−change, 0), each smoothed with RMA(n), seeded over changes 1 to n. RSI = 100 − 100 / (1 + avg gain / avg loss), and 100 when the average loss is 0. Checked against StockCharts' published 14-period worked example (all 19 values match to 0.01).
- **MACD(12, 26, 9):** MACD line = EMA(12) − EMA(26) of the close. Signal = EMA(9) of the MACD line, seeded on its first 9 valid values.
- **Bollinger(20, 2):** middle = SMA(20). Lower = middle − 2·σ, where σ is the population standard deviation (divisor n) of the last 20 closes, as John Bollinger specifies.
- **Donchian:** highest high of bars t−20 … t−1 and lowest low of bars t−10 … t−1. The current bar is left out, and its close is compared with the levels.
- **True range:** max(high − low, |high − previous close|, |low − previous close|), and high − low on the first bar.
- **ATR(n), Wilder:** RMA(n) of the true range, seeded with the mean of the first n true ranges.
- **Supertrend(10, 3)** (TradingView's construction):
  - Bands: basic upper = (high + low)/2 + 3·ATR(10), and basic lower = (high + low)/2 − 3·ATR(10).
  - Final upper band: the basic upper band if it is below the previous final upper band, or if the previous close was above that band; otherwise the previous final upper band. The final lower band mirrors this.
  - Trend: it starts down on the first bar with an ATR. A down trend turns up when the close is above the final upper band; an up trend turns down when the close is below the final lower band.
- **Parabolic SAR(0.02, 0.2)** (Wilder's, as TA-Lib's `TA_SAR` computes it):
  - Acceleration factor (AF): starts at 0.02, rises 0.02 with each new extreme point (EP), and is capped at 0.2.
  - First trend (bar 1): short if bar 1's down move (previous low − low) is positive and larger than its up move (high − previous high), else long. A long starts with SAR = bar 0's low and EP = bar 1's high; a short with SAR = bar 0's high and EP = bar 1's low.
  - Flips: a long flips short when the low touches or crosses the SAR (low ≤ SAR), and a short flips long when the high touches or crosses it (high ≥ SAR). On a flip, the SAR restarts at the prior EP, kept beyond the current and previous bar's range.
  - Next SAR = SAR + AF·(EP − SAR), kept beyond the current and previous bar's range: at or below their lows while long, at or above their highs while short.
- **Stochastic(14, 3, 3):** fast %K = 100·(close − lowest low of 14) / (highest high of 14 − lowest low of 14), the current bar included. Slow %K = SMA(3) of fast %K. Slow %D (the second 3) is not used by the rule.
- **Keltner:** middle = EMA(20) of the close; upper = middle + 2·ATR(10).
- **Momentum 12-1:** close[t−21] / close[t−252] − 1, in trading days, on split-adjusted closes.

## Where a definition could not be implemented exactly as written

1. **Momentum 12-1, the month's last trading day.** The code has no exchange calendar, and it must not read the next bar's date (a look-ahead). It therefore takes a month's last trading day to be its last weekday (Mon–Fri), from each bar's own date. When that weekday is an exchange holiday there is no bar on it. The decision is then made on the first bar of the new month instead: signal at that bar's close, fill at the next open, one trading day late. Between 1999-03 and 2026-12 this happens in eight months, all in the development window and none in the hold-out:
   - Good Friday: 2002-03-29, 2013-03-29, 2018-03-30, 2024-03-29.
   - Memorial Day: 1999-05-31, 2004-05-31, 2010-05-31, 2021-05-31.
2. **Momentum 12-1, the return.** The signal is a price return on split-adjusted closes. Dividends are not in the price series, so they are not in the signal; they are still credited to the position's cash. QQQ's dividend yield is small, so only a return very close to zero could change sign.
3. **Turtle System 1** is the stated close rule only. The original system's 2N stop, unit sizing, skip-after-a-winning-breakout filter and 55-day failsafe are not part of the definition and are not added.
4. **Parabolic SAR, Supertrend and EMA** have several published variants: the first trend, whether a touch counts as a flip, and the EMA seed. Each choice above follows a named reference (TA-Lib, TradingView, and the TA-Lib SMA seed). The choices only change the first bars and rare exact ties.
5. **Helpers.** The contract offers indicator helpers (`ta`, `qw_features.technical`). They are not used: every formula is written in plain numpy/pandas in the strategy file, so the published code is the whole definition.

## How to read the results

- **Grade and trials.** All twelve development runs are in one study on QQQ 1d. The product counts each run as a trial, plus this account's other recent QQQ 1d runs (`grade.search`), when it grades a result. Strategies run later in the file order (01 → 12) are therefore graded against more trials. The ledger gives the trial count each result reports (`grade.trials`).
- **Withheld figures.** The product withholds figures from any run of fewer than 10 trades, and always withholds the buy-and-hold return (market-data licence). The ledger writes "withheld: <reason>" where a figure is withheld, and "not reported" where a field is absent.

## Local verification (before any run)

All of it was run on synthetic data, seeded random walks with no market data, using a local Python environment (backtesting.py 0.3.3, pandas 2.2.3, numpy 2.1.3). There are 72 tests in `tests/`:

- **The product's gate.** Every file passes the product's own AST guard, RestrictedPython compile and sandbox namespace.
- **The product's engine.** Every file runs through the product's own engine with the default equity costs. Its trades fall on the same bars as plain backtesting.py, and each trade's cost is 0.5 bp + 1 bp + 1 bp of the trade value.
- **Fills and positions.** Every strategy trades, goes long only, holds one position at a time, and fills at the next bar's open.
- **No look-ahead.** With the data cut at three points, every indicator value and every decision before the cut is unchanged.
- **Rule replay.** For strategies 1–11, the trades equal an independent replay of the stated rule from the same indicators. For strategy 12, decisions fall on each month's last trading day, including the holiday fallback, and the position follows the sign of the momentum.
- **Indicator values.** RSI matches StockCharts' published example and converges to the `ta` library's RSI. EMA converges to pandas `ewm`. ATR, Bollinger, Donchian, Stochastic, Supertrend and Parabolic SAR match hand-computed values, including the SAR flip boundary and the clamp after a flip.
- **The tests can fail.** A `.shift(-1)` on the 20-bar high, a centred rolling mean, a changed exit level and an order delayed one bar were each caught.

## Fixed before any run (2026-10-28, 22:20 EET): grading pass, held-out order, tier rule

- **Second grading pass.** The product grades each run against the trials counted so far, so in one pass strategy 01
  would be graded against 1 trial and strategy 12 against 12. After all twelve development runs, each one is run
  again, unchanged. A byte-for-byte repeat is not a new candidate in the product, so the count stays at twelve, and
  every strategy is graded against the full search. The ledger uses the second pass. The first pass is kept on
  file. If the second pass shows a different trial count from the first pass's last run, that is
  reported.
- **Held-out order.** The first held-out test is the one the product counts (once per account and market). It goes to
  the strategy with the highest Honesty Score in the second pass, among those whose `hold_out_estimate` is at least 10
  trades, so the counted test is not spent on a hold-out too short to show figures. Ties go to more development
  trades, then to the lower file number. The other eleven follow in file order and are reported as "not the counted
  test". Picking among them afterwards would be a second search on the same months.
- **Tier rule (for the tier list).** It uses the facts each result states, never taste or a figure the protocol keeps
  out of public text. Terms:
  - *made money* = the run's net result after costs is above zero;
  - *beat holding* = the result's own buy-and-hold comparison says it did better;
  - *enough trades* = at least 30 development trades and at least 10 held-out trades (the product's floor for showing
    figures).

  The tiers, checked from F upwards:
  - **F:** did not make money over the development window.
  - **D:** made money over the development window, but on fewer than 30 trades (too thin to judge).
  - **C:** made money over the development window with enough trades, then lost money on the hold-out.
  - **B:** made money over the development window with enough trades; the hold-out had too few trades to judge.
  - **A:** made money in both windows with enough trades, but did not beat holding in both.
  - **S:** made money and beat holding in both windows, with enough trades in both.

  The tier is not the product's grade. Every strategy's grade stays at C or below except the one counted held-out test.
  Public pieces say "tier" and "grade" separately.

## SHA-256 of each strategy file

```
918eccd6851cf015b3c4592fae89380061eee29994046365f54a1cdbae1f37c0  strategies/01_rsi2.py
34ee64a8a3700054e0d0812d520edd8e5133de42f5bf489474c5114fa285ed80  strategies/02_rsi14.py
eba0bfaaaa764f332883c9b21e79a4f7563d50123b14bce9a2265a5c480d591a  strategies/03_macd.py
4a6f5086a9acd1a393e13b3ea5eb63b894712034936593f60a79849dea74dd34  strategies/04_golden_cross.py
3f894d90a4dd5dd6cb03bfa642d1b6e2ca6226f7f4121c420b111e28ad48ac05  strategies/05_ema_9_21.py
c4a0d4f804e3b33cc3fb51c7723790c0e722ac61e4f83d5bb7e9b268870b257f  strategies/06_bollinger.py
a6e8e7290be5f34b4c1ddc6af857603ae70739d77f32c9579c7084fb5172860b  strategies/07_donchian.py
b23f395d20bbe9d4fa9d25cdaf23af956998fc1ef5c6a543dc543a805566d3a9  strategies/08_supertrend.py
a7cdc5128deef3c54100b7e37cdf489af9189c1217763fc6d46a71b24685e1af  strategies/09_parabolic_sar.py
8146121862a610b083a6684e67c1caedf3aadef4a0cafbce6a1d3032ad31cb3e  strategies/10_stochastic.py
95b39462b2495e871631ec687de0c22ef5bac4a2d696db1ec783b8a2c71f3ef4  strategies/11_keltner.py
17f75e5c715906fecc370093c1648b2776f5577b62ddc353f183ea20e48e9c02  strategies/12_tsmom_12_1.py
```

## After the runs (2026-10-28, 22:45 EET): what the second pass did

The second pass changed nothing. The product replays an identical run from its first result (`replayed_from`), and
the replay keeps that run's grade and trial count. The grades in the ledger are therefore as the product computed
them at the time: strategy 01 against 1 trial, up to strategy 12 against 12. The tier rule does not use the grade,
so the tiers are unaffected. Every public piece that quotes a grade gives its trial count with it.
The held-out order followed the rule: 05 first (score 62 with an expected 10 held-out trades), then 01–04 and 06–12.
