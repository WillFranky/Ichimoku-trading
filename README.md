# Ichimoku-trading

Part 1

This implementation is Work-in-Progress for learning purposes. The code is not ready and need to be cleaned up. Bugs may exist.

Not intended for production use. 

Please note - this project uses yfinance which has been deprecated (Although still works). Yfinance is unstable which impacts the results. 

Idea:

The idea with this project is to formulate a simple strategy, with high hit rate and low drawdown. It is not intended for automatic algorithmic trading, but for identifying triggers in the market to act upon. 

Most long term investors make their largest gains in a small duration of time when stocks or markets rally.For this reason, the chosen strategy is a Momentum-based strategy, intended to be used when markets/instruments are trending. 

The buy signal script does currently not include selling, as this is only intended as a screener.
A backtest is provided (ofc including selling signal), to validate this as a strategy.

"If you are going to follow the herd, make sure you are not last in line"

This project aims to provide early notification, so that positions can be opened quickly enough, and closed quickly enough, to maximize profits.

Use cases are:
- Dedicating a small share of a larger portfolio to achieve additional gains when there is strong momentum (Especially useful if the long term portfolio is allocateed elsewhere)
- Effectively deploying limited amount of capital to get significant returns
- Potentially it could be a way for a fundamental investor to benefit from assets otherwise less interesting (e.g. Crypto, Meme-stocks, etc)
- ...

Backtest results (07.06.2024):
- Nvidia from 2023-01-01 to 2024-06-01 (Strong trend since ~2022):
  8 trades
  390% return
  Max drawdown: 23,8%

- Tesla from 2021-01-01 to 2024-06-01 (Lower priced at end of period than beginning):
  6 trades
  130% profit (171% max)
  Max drawdown -24%
  (If buy and hold would have been used for this time frame, returns would have been approx. -28%)

Future use cases to be evaluated:
- Implement sell signal for open positions
- Modifying for short-selling in downtrending markets
- Trading Crypto & FX?
- Trading automation against demo account
- Use reliable source of data instead of Yfinance

Backlog:
- ...
- ...
- ...


Ichimoku strategy explained:
- Tenkan-sen = Time-series averaging of maximum and minimum of last 9 periods
- Kijun-sen = Time-series average of maximum and minimum of last 26 periods
- Senkou-Span A (=cloud Span A) = Time-series average of Tenkan-sen and Kijun-sen, shifted 26 periods in time
- Senkou-Span B (=cloud Span B) = Time-series average of Tenkan-sen and Kijun-sen, shifted 52 periods in time
- Chikou-Span = Price shifted 26 periods in time

- Additionally, resistances levels are defined through unsupervised clustering. This is intended to be indicative, as this may not be exact, although clustering is the best approach I have found for identifying support and resistance levels.
  
Buy Signal:
- Price is above Senkou-Span A (Kumo break)
- Senkou-Span A is above Senkou-Span B   
- Price is above highest identified resistance level or has more than 10% margin to resistance   (To prevent triggers for stocks near resistance)

Sell Signal (only backtest):
- Price hits Senkou Span A





Part2

The ichimoku strategy works well but has one significant flaw, it uses historic data. The strategy can be likened to a moving freight train. It takes time for it to get up to speed, but at least we know that once it is up to speed, it will take a while for it to come to a halt, which enables us to catch decelleration in time.

If we are OK with driving while looking in the rear view mirror and if we are willing to accept incurrent losses of things we dont see in time, then this is a good strategy. 

Important questions remain: Because the strategy isn't implemented to automatically trade, we cannot be certain that we always take a long position at the right moment. And we would like to project what is infront of us. We may identify opportunities where instruments are far into their breakouts. Do we then take the position and chase the price at already high levels? What if we see negative divergences in indicators or volumes?

It would be a big help if we could decide if the trade would be profitable based on a statistical model and historic data.


Tbc...


- Strategy: Random Forest?
- Features:
  * Distance from Price to Senkou Span A and Senkou Span B (height over Span A and width between bands)
  * Crossovers of Tenkan-sen and Kijun-sen
  (still only considering long positions where price is above Span A)

  Indicators? Volume? ....?
