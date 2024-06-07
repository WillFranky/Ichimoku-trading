# Ichimocku-trading

This implementation is Work-in-Progress for learning purposes. The code is not ready and need to be cleaned up. Bugs may exist.

Not intended for production use. 

Idea:


Most long term investors make their largest gains in a small duration of time when stocks or markets rally. The idea with this project is to formulate a simple strategy, with high hit rate and low drawdown. It is not intended for automatic algorithmic trading, but for identifying triggers in the market to act upon. 

The chosen strategy is a Momentum-based strategy. 

The buy signal script does currently not include selling, as this is only intended as a screener.
A backtest is provided (ofc including selling signal), to validate this as a strategy.

Use cases are:
- Dedicating a small share of a larger portfolio to achieve additional gains when there is strong momentum (Especially useful if the long term portfolio is allocateed elsewhere)
- Effectively deploying limited amount of capital to get significant returns
- Potentially it could be a way for a fundamental investor to benefit from assets otherwise less interesting (e.g. Crypto, Meme-stocks, etc)
- ...

Future use cases to be evaluated:
- Modifying for hort-sell in downtrending markets
- Trading Crypto & FX?

Backlog:
- ...
- ...
- ...


Ichimocku strategy explained:
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
