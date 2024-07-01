# Ichimoku-trading

Part 1 - Ichimoku trading algorithm implementation

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
- ..

Files:
  Ichimoku buy triggers.py - Main file
  Ichimoku backtest.py - Backtest file
  Backtest NVIDIA.html - Export of backtest result
  BAcktest TSLA.html - Export of backtest result

Backtest results (07.06.2024):
- Nvidia from 2022-01-01 to 2024-06-01 (Strong trend since ~2022):
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
- Check and fix lagging
- Streamline inefficient code - loading stock information from yFinance - Done 26.06.2024
- Fix buy trigger constraint for senkou span - Done 14.06.2024
- Fix incomplete data series for Ichimoku spans calculation - Done 14.06.2024
- Structure code and remove redundant code
- Implement sell triggers for existing positions
- Implement trading strategy(?)
- Implement position sizing(?)
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





Part2 - Using Machine Learing to predict trade probability of success

The ichimoku strategy works well but has some significant flaws. It uses historic data, and although it looks to be performing well, most breakouts fail. Backtest results are deterministic, ML algorithms are probabilistic. This means - we do not know the actual likelihood of outcome in Part 1 we just know the actual results of what has already happened. This is where ML can help in answering the questions, is this a good trade to take and what position size (=risk) is involved in this trade?

To improve the model, we would like to know the probability of a trade being successful and we would like to know the parameters which affects the probability of a positive outcome.

- I want to predict: The probability of the trade yielding at least 20% profit in 30 days.
- The script screens all s&p500 stocks and gives me a shortlist of stocks where probability is deemed to be over 50%.
- Features used: 'macd', 'Volume', 'senkou_span_a', 'rsi', 'stochastic', 'pe_ratio', 'growth_rate'. 
- The mdoel uses 10 years of data

Performance (ticker SMCI):
- Accuracy: 0.67 (=67% ability to predict correctly)
- Precision: 0.63 (=63% ability to identify positive outcomes)
- Recall: 0.22 (=22% ability to identify true positives - to be improved)
- F1 Score: 0.33

Collinearity / VIF:
- MACD: 2.061204
- Volume: 3.019751
- Senkou Span A: 2.097778
- RSI: 3.202211
- Stochhastic: 2.978582
-  P/E Ratio: 16.707104
-  Earnings growth rate: 1.427803

Result (SMCI, last 6 months):
2024-01-19: 0.99
2024-01-22: 0.98
2024-01-23: 0.65
2024-01-24: 0.80
2024-01-29: 0.71
2024-01-30: 0.96
2024-01-31: 0.75
2024-02-01: 0.81
2024-02-02: 0.73
2024-02-05: 0.94
2024-02-06: 0.95
2024-02-07: 0.69
2024-02-09: 0.54
2024-02-12: 0.90
2024-02-13: 0.79
2024-02-14: 0.95
2024-02-15: 0.99
2024-02-16: 1.00
2024-02-20: 0.99
2024-02-21: 0.86
2024-02-22: 0.99
2024-02-23: 0.95
2024-03-04: 0.95
2024-03-05: 0.64
2024-03-15: 0.85
2024-03-18: 0.54
2024-03-19: 0.56
2024-04-19: 0.96
2024-04-22: 0.61
2024-04-23: 0.52
2024-05-01: 0.87
2024-05-23: 0.65
2024-06-13: 0.69
2024-06-20: 0.79
2024-06-28: 0.93

In general, the predicitons seem to be correct.

Outcomes:
- A first ML model in predicting trade probabilities.
- The model needs more tweaking to improve its performance.
- As interesting as the model is, it may not be the correct approach or may need additional adjustments to fit the use case set out in the initial problem. It was assumed that the majority of profits are realized when markets/stocks are breaking out, and that majority of breakouts fail. If a breakout is likened to a Tsunami, it may not be the best approach to consider tidal waves and daily noise in predicting these(?). E.g. Given how rare these events are, are datasets large enough to capture breakouts? Are there other factors to take into account which are more important?


Notes / learnings:
- Financial data science has inherent problem in messy data. (e.g. tickers changing, split adjustments, dividends, outliers, look-ahead bias...
- Linear and logistic regression models are too simplistic. They are good if the number of features is low ~<10
- Deep learning is too complicated for financial ML.
- Random Forest has the right level of complexity (100-1000 features)
- Feature engineering is a HIGHLY manual process. Requires deep financial market knowledge to be done properly. (=domain knowledge is crucial in ML)
- Stationarity is a necessity, models need to be trained on what they will predict. Indices are not stationary, backtest results are.

Predicting the stock market certainly is complicated, and will inevitably go wrong to some extent - Focusing on predicting outcome of trading strategy is a better bet.




Part 3 - Improvements to the Machine Learning algorithm
Adjusting algorithm to predict outcome of Ichimoku strategy and focusing on breakouts.

TBC...


