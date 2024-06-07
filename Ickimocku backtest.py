import numpy as np
import pandas as pd
import yfinance as yf
from backtesting import Backtest, Strategy
from sklearn.cluster import KMeans
from scipy.signal import find_peaks

def calculate_senkou_span(hist_data):
    hist_data['High'] = hist_data['High'].shift(1)
    hist_data['Low'] = hist_data['Low'].shift(1)

    high_9 = hist_data['High'].rolling(window=9).max()
    low_9 = hist_data['Low'].rolling(window=9).min()
    tenkan_sen = (high_9 + low_9) / 2

    high_26 = hist_data['High'].rolling(window=26).max()
    low_26 = hist_data['Low'].rolling(window=26).min()
    kijun_sen = (high_26 + low_26) / 2

    high_52 = hist_data['High'].rolling(window=52).max()
    low_52 = hist_data['Low'].rolling(window=52).min()

    senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(periods=26)
    senkou_span_b = ((high_52 + low_52) / 2).shift(periods=26)
    chikou_span = hist_data['Close'].shift(-26)

    return senkou_span_a, senkou_span_b, chikou_span

def get_resistance_levels(stock_data):
    peaks, _ = find_peaks(stock_data['Close'].values)
    maxima_prices = stock_data['Close'].values[peaks]
    maxima_times = np.linspace(0, 1, len(stock_data))[peaks]

    if maxima_prices.size == 0:
        return None

    highest_maxima = maxima_prices.max()

    X_time = np.linspace(0, 1, len(stock_data)).reshape(-1, 1)
    X_price = (stock_data['Close'].values - np.min(stock_data['Close'])) / (np.max(stock_data['Close']) - np.min(stock_data['Close']))
    
    X_cluster = np.column_stack((X_time, X_price))
    maxima_normalized = (maxima_prices - np.min(stock_data['Close'])) / (np.max(stock_data['Close']) - np.min(stock_data['Close']))
    maxima_data = np.column_stack((maxima_times, maxima_normalized))
    X_cluster = np.vstack((X_cluster, maxima_data))

    num_clusters = 5
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(X_cluster)

    cluster_centers = kmeans.cluster_centers_[:, 1] * (np.max(stock_data['Close']) - np.min(stock_data['Close'])) + np.min(stock_data['Close'])

    current_price = stock_data['Close'].values[-1]
    resistance_levels = cluster_centers[cluster_centers > current_price * 0.9]

    if highest_maxima > current_price:
        resistance_levels = np.append(resistance_levels, highest_maxima)
        resistance_levels = np.unique(resistance_levels)
   
    return resistance_levels

class IchimokuStrategy(Strategy):
    def init(self):
        self.senkou_span_a, self.senkou_span_b, self.chikou_span = self.I(calculate_senkou_span, self.data.df)
        self.resistance_levels = get_resistance_levels(self.data.df)

    def next(self):
        price = self.data.Close[-1]
        nearest_resistance = min([level for level in self.resistance_levels if level > price], default=None)

        if nearest_resistance is not None:
            margin_up = round(100 * (nearest_resistance - price) / price, 2)
        else:
            margin_up = 0
            nearest_resistance = 0

        senkou_span_a_value = self.senkou_span_a[-1]
        senkou_span_b_value = self.senkou_span_b[-1]
        chikou_span_value = self.chikou_span[-26]  # Chikou Span is 26 periods behind

        if senkou_span_a_value is not None and senkou_span_b_value is not None and chikou_span_value is not None:
            if price > senkou_span_a_value:
                if price < chikou_span_value:
                    if senkou_span_a_value > senkou_span_b_value:
                        if price > nearest_resistance or price < 0.9 * nearest_resistance:
                            if not self.position:  # Only open a new position if there is none
                                self.buy()
            else:
                if self.position:  # Close the position if the price falls below Senkou Span A
                    self.position.close()
            
    def plot(self, ax):
        ax.plot(self.data.index, self.senkou_span_a, label='Senkou Span A', color='green')
        #ax.plot(self.data.index, self.senkou_span_b, label='Senkou Span B', color='red')
        ax.plot(self.data.index, self.chikou_span, label='Chikou Span', color='orange')
        ax.legend()

symbol = 'ABBV'
start_date = '2021-01-01'
end_date = '2024-06-01'

data = yf.download(symbol, start=start_date, end=end_date)

bt = Backtest(data, IchimokuStrategy, cash=10000, commission=.002)
stats = bt.run()

# Run the backtest and plot the results
bt.plot()
