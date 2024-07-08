<h1># Ichimoku-trading</h1>

<h2>Part 1 - Ichimoku trading algorithm implementation</h2>

This implementation is Work-in-Progress for learning purposes. The code is not ready and need to be cleaned up. Bugs may exist.

Not intended for production use. 

<h3>Idea:</h3>

The idea with this project is to formulate a simple strategy, with high hit rate and low drawdown. It is not intended for automatic algorithmic trading, but for identifying triggers in the market to act upon. 

Most long term investors make their largest gains in a small duration of time when stocks or markets rally.For this reason, the chosen strategy is a Momentum-based strategy, intended to be used when markets/instruments are trending. 

The buy signal script does currently not include selling, as this is only intended as a screener.
A backtest is provided (ofc including selling signal), to validate this as a strategy.

"If you are going to follow the herd, make sure you are not last in line"

This project aims to provide early notification, so that positions can be opened quickly enough, and closed quickly enough, to maximize profits.
<br>

<h3>Use cases are:</h3>
<ul>
<li> Dedicating a small share of a larger portfolio to achieve additional gains when there is strong momentum (Especially useful if the long term portfolio is allocateed elsewhere)</li>
<li> Effectively deploying limited amount of capital to get significant returns</li>
<li> Potentially it could be a way for a fundamental investor to benefit from assets otherwise potentially less interesting (e.g. Crypto, Meme-stocks, etc)</li>
<li> ..</li>
</ul>
<br>

<h3>Files:</h3>
  <ul>
<li>Ichimoku buy triggers.py - Main file</li>
<li>  Ichimoku backtest.py - Backtest file</li>
<li>  Backtest NVIDIA.html - Export of backtest result</li>
<li>  BAcktest TSLA.html - Export of backtest result</li>
</ul>
<br>

<h3>Backtest results (07.06.2024):</h3>
<ul>
<li>Nvidia from 2022-01-01 to 2024-06-01 (Strong trend since ~2022):</li>
<ul> <li> 8 trades </li><li>  390% return </li><li>   Max drawdown: 23,8%</li>
</ul>
</ul><ul>


<li>Tesla from 2021-01-01 to 2024-06-01 (Lower priced at end of period than beginning):</li>
   <ul><li>6 trades</li><li>  130% profit (171% max)</li><li>   Max drawdown -24%</li><li>  
  (If buy and hold would have been used for this time frame, returns would have been approx. -28%)
   </li></ul> 
</ul>
<ul>
<h3>Future use cases to be evaluated:</h3>
<ul>
<li>Implement sell signal for open positions</li>
<li>Modifying for short-selling in downtrending markets</li>
<li>Trading Crypto & FX?</li>
<li>Trading automation against demo account</li>
<li>Use reliable source of data instead of Yfinance</li>
</ul>
<br>
  
<h3>Backlog:</h3>
<ul>
<li>Check and fix lagging</li>
<li>Streamline inefficient code - loading stock information from yFinance - Done 26.06.2024</li>
<li>Fix buy trigger constraint for senkou span - Done 14.06.2024</li>
<li>Fix incomplete data series for Ichimoku spans calculation - Done 14.06.2024</li>
<li>Structure code and remove redundant code</li>
<li>Implement sell triggers for existing positions</li>
<li>Implement trading strategy(?)</li>
<li>Implement position sizing(?)</li>
<li>...</li>
</ul>
<br>

<h3>Ichimoku strategy explained:</h3>
<ul>
<li>Tenkan-sen = Time-series averaging of maximum and minimum of last 9 periods</li>
<li>Kijun-sen = Time-series average of maximum and minimum of last 26 periods</li>
<li>Senkou-Span A (=cloud Span A) = Time-series average of Tenkan-sen and Kijun-sen, shifted 26 periods in time</li>
<li>Senkou-Span B (=cloud Span B) = Time-series average of Tenkan-sen and Kijun-sen, shifted 52 periods in time</li>
<li>Chikou-Span = Price shifted 26 periods in time</li>
<li></li>
<li>Additionally, resistances levels are defined through unsupervised clustering. This is intended to be indicative, as this may not be exact, although clustering is the best approach I have found for identifying support and resistance levels.</li>
</ul>
<br>

Buy Signal:
<ul>
<li>Price is above Senkou-Span A (Kumo break)</li>
<li>Senkou-Span A is above Senkou-Span B   </li>
<li>Price is above highest identified resistance level or has more than 10% margin to resistance   (To prevent triggers for stocks near resistance)</li>
</ul>
<br>

Sell Signal (only backtest):
<ul><li>Price hits Senkou Span A</li></ul>



<h2>Part2 - Using Machine Learing to predict trade probability of success</h2>

The ichimoku strategy works well but has some significant flaws. It uses historic data, and although it looks to be performing well, most breakouts fail. Backtest results are deterministic, ML algorithms are probabilistic. This means - we do not know the actual likelihood of outcome in Part 1 we just know the actual results of what has already happened. This is where ML can help in answering the questions, is this a good trade to take and what position size (=risk) is involved in this trade?

To improve the model, we would like to know the probability of a trade being successful and we would like to know the parameters which affects the probability of a positive outcome.

<ul>
<li>I want to predict: The probability of the trade yielding at least 20% profit in 30 days.</li>
<li>The script screens all s&p500 stocks and gives me a shortlist of stocks where probability is deemed to be over 50%.</li>
<li>Features used: 'macd', 'Volume', 'senkou_span_a', 'rsi', 'stochastic', 'pe_ratio', 'growth_rate'. </li>
<li>The model uses 10 years of data</li>
</ul>
<br>

Performance (ticker SMCI):
<ul>
<li>Accuracy: 0.67 (=67% ability to predict correctly)</li>
<li>Precision: 0.63 (=63% ability to identify positive outcomes)</li>
<li>Recall: 0.22 (=22% ability to identify true positives - to be improved)</li>
<li>F1 Score: 0.33</li>
</ul>
<br>

Collinearity / VIF:
<ul>
<li>MACD: 2.061204</li>
<li>Volume: 3.019751</li>
<li>Senkou Span A: 2.097778</li>
<li>RSI: 3.202211</li>
<li>Stochhastic: 2.978582</li>
<li>P/E Ratio: 16.707104</li>
<li>Earnings growth rate: 1.427803</li>
</ul>
<br>
Result (SMCI, last 6 months):
<table>
<thead><tr><td>Date</td><td>Probability</td></tr></thead>
<tbody>
<tr><td>2024-01-19:</td><td>0.99</td></tr>
<tr><td>2024-01-22:</td><td>0.98</td></tr>
<tr><td>2024-01-23:</td><td>0.65</td></tr>
<tr><td>2024-01-24:</td><td>0.80</td></tr>
<tr><td>2024-01-29:</td><td>0.71</td></tr>
<tr><td>2024-01-30:</td><td>0.96</td></tr>
<tr><td>2024-01-31:</td><td>0.75</td></tr>
<tr><td>2024-02-01:</td><td>0.81</td></tr>
<tr><td>2024-02-02:</td><td>0.73</td></tr>
<tr><td>2024-02-05:</td><td>0.94</td></tr>
<tr><td>2024-02-06:</td><td>0.95</td></tr>
<tr><td>2024-02-07:</td><td>0.69</td></tr>
<tr><td>2024-02-09:</td><td>0.54</td></tr>
<tr><td>2024-02-12:</td><td>0.90</td></tr>
<tr><td>2024-02-13:</td><td>0.79</td></tr>
<tr><td>2024-02-14:</td><td>0.95</td></tr>
<tr><td>2024-02-15:</td><td>0.99</td></tr>
<tr><td>2024-02-16:</td><td>1.00</td></tr>
<tr><td>2024-02-20:</td><td>0.99</td></tr>
<tr><td>2024-02-21:</td><td>0.86</td></tr>
<tr><td>2024-02-22:</td><td>0.99</td></tr>
<tr><td>2024-02-23:</td><td>0.95</td></tr>
<tr><td>2024-03-04:</td><td>0.95</td></tr>
<tr><td>2024-03-05:</td><td>0.64</td></tr>
<tr><td>2024-03-15:</td><td>0.85</td></tr>
<tr><td>2024-03-18:</td><td>0.54</td></tr>
<tr><td>2024-03-19:</td><td>0.56</td></tr>
<tr><td>2024-04-19:</td><td>0.96</td></tr>
<tr><td>2024-04-22:</td><td>0.61</td></tr>
<tr><td>2024-04-23:</td><td>0.52</td></tr>
<tr><td>2024-05-01:</td><td>0.87</td></tr>
<tr><td>2024-05-23:</td><td>0.65</td></tr>
<tr><td>2024-06-13:</td><td>0.69</td></tr>
<tr><td>2024-06-20:</td><td>0.79</td></tr>
<tr><td>2024-06-28:</td><td>0.93</td></tr>
</tbody>
</table>

In general, the predicitons seem to be correct.

Outcomes:
- A first ML model in predicting trade probabilities.
- The model needs more tweaking to improve its performance.
- As interesting as the model is, it may not be the correct approach or may need additional adjustments to fit the use case set out in the initial problem. It was assumed that the majority of profits are realized when markets/stocks are breaking out, and that majority of breakouts fail. If a breakout is likened to a Tsunami, it may not be the best approach to consider tidal waves and daily noise in predicting these(?). E.g. Given how rare these events are, are datasets large enough to capture breakouts? Are there other factors to take into account which are more important?
- In the current setup, the results are influenced by the sample size - to be revisited.


Notes / learnings:
- Financial data science has inherent problem in messy data. (e.g. tickers changing, split adjustments, dividends, outliers, look-ahead bias...
- Linear and logistic regression models are simple (too simplistic?). They are good if the number of features is low ~<10
- Deep learning is too complicated for financial ML.
- Random Forest might have (?) the right level of complexity for more professional algorithms (100-1000 features)
- Feature engineering is a HIGHLY manual process. Requires deep financial market knowledge to be done properly. (=domain knowledge is crucial in ML)
- Stationarity is a necessity, models need to be trained on what they will predict. Indices are not stationary, backtest results are.

Predicting the stock market certainly is complicated, and will inevitably go wrong to some extent - Focusing on predicting outcome of trading strategy is a better bet.




<h2>Part 3 - Improvements to the Machine Learning algorithm</h2>
Adjusting algorithm to predict outcome of Ichimoku strategy and focusing on breakouts.

TBC...


