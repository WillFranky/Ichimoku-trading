import pandas as pd
import numpy as np
import yfinance as yf
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import requests


    # --- FEATURES --- #

def calculate_ichimoku_features(data):
    high_9 = data['High'].rolling(window=9).max()
    low_9 = data['Low'].rolling(window=9).min()
    data['tenkan_sen'] = (high_9 + low_9) / 2

    high_26 = data['High'].rolling(window=26).max()
    low_26 = data['Low'].rolling(window=26).min()
    data['kijun_sen'] = (high_26 + low_26) / 2

    data['senkou_span_a'] = ((data['tenkan_sen'] + data['kijun_sen']) / 2).shift(26)
    high_52 = data['High'].rolling(window=52).max()
    low_52 = data['Low'].rolling(window=52).min()
    data['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

    data['chikou_span'] = data['Close']

    return data

def calculate_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    return data

def calculate_stochastic(data, window=14):
    low_min = data['Low'].rolling(window=window).min()
    high_max = data['High'].rolling(window=window).max()
    data['stochastic'] = 100 * (data['Close'] - low_min) / (high_max - low_min)
    return data

def calculate_fibonacci_retracement(data):
    high_price = data['High'].max()
    low_price = data['Low'].min()
    difference = high_price - low_price
    data['fib_23.6'] = high_price - (difference * 0.236)
    data['fib_38.2'] = high_price - (difference * 0.382)
    data['fib_50.0'] = high_price - (difference * 0.5)
    data['fib_61.8'] = high_price - (difference * 0.618)
    data['fib_100'] = high_price
    data['fib_0'] = low_price
    return data

def calculate_pe_ratio(data, symbol):
    ticker = yf.Ticker(symbol)
    try:
        pe_ratio = ticker.info['trailingPE']
        eps = data['Close'] / pe_ratio
        data['pe_ratio'] = data['Close'] / eps
    except KeyError:
        print(f"PE ratio data not available for {symbol}.")
        data['pe_ratio'] = np.nan
    return data

def calculate_growth_rate(data, symbol):
    ticker = yf.Ticker(symbol)
    try:
        financials = ticker.financials
        if 'Total Revenue' in financials.index:
            revenue = financials.loc['Total Revenue']
            growth_rate = revenue.pct_change(fill_method=None).fillna(0) * 100
            growth_rate.replace([np.inf, -np.inf], 0, inplace=True)
            growth_rate = growth_rate.fillna(0)
            growth_rate = growth_rate.resample('D').ffill().reindex(data.index, method='ffill')
            growth_rate = growth_rate.infer_objects(copy=False)  # Ensure correct dtype
            data['growth_rate'] = growth_rate
        else:
            print(f"Total Revenue data not available for {symbol}.")
            data['growth_rate'] = np.nan
    except ValueError as e:
        print(f"Value error retrieving growth rate data for {symbol}: {str(e)}")
        data['growth_rate'] = np.nan
    except Exception as e:
        print(f"Unexpected error retrieving growth rate data for {symbol}: {str(e)}")
        data['growth_rate'] = np.nan
    return data


def get_sp500_symbols():
    """
    Retrieves the list of S&P 500 stock symbols from Wikipedia.
    """
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable sortable'})
    symbols = []
    for row in table.find_all('tr')[1:]:
        symbol = row.find_all('td')[0].text.strip()
        symbols.append(symbol)
    
    # RAW MATERIALS
    silver_ticker = 'SLV' #iShares Silver Trust ETF
    gold_ticker = 'GLD' #SPDR Gold Shares ETF
    oil_ticker = 'USO' #United States Oil Fund ETF
    natural_gas_ticker = 'UNG' #United States Natural Gas Fund ETF
    copper_ticker = 'JJC' #iPath Series B Bloomberg Copper Subindex Total Return ETN
    essential_metals_ticker = 'DBB' #Invesco DB Base Metals Fund ETF
    
    symbols.extend([silver_ticker, gold_ticker, oil_ticker, natural_gas_ticker, copper_ticker, essential_metals_ticker])
    
    return symbols


def get_realtime_stock_data(symbol):
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')  # Yesterday's date
    start_date = (datetime.now() - timedelta(days=365 * 10)).strftime('%Y-%m-%d')  
    
    try:
        data = yf.download(symbol, start=start_date, end=end_date)
        if data.empty:
            print(f"No price data available for {symbol} on {end_date}.")
            return None
        
        data = calculate_ichimoku_features(data)
        data['macd'] = data['Close'].ewm(span=12, adjust=False).mean() - data['Close'].ewm(span=26, adjust=False).mean()
        data = calculate_rsi(data)
        data = calculate_stochastic(data)
        data = calculate_fibonacci_retracement(data)
        data = calculate_pe_ratio(data, symbol)
        data = calculate_growth_rate(data, symbol)
        
        data = data.dropna()
        
        if data.empty:
            print(f"No valid data after processing for {symbol}.")
            return None
        
        return data
    
    except Exception as e:
        print(f"Error retrieving data for {symbol}: {str(e)}")
        return None
    


def generate_features_and_targets(data, profit_target=0.20, look_ahead_period=30):
    data = data.copy()  
    
    data['future_max'] = data['Close'].rolling(window=look_ahead_period).max().shift(-look_ahead_period)
    data['target'] = (data['future_max'] >= data['Close'] * (1 + profit_target)).astype(int)
    
    #features = data[['macd', 'Volume', 'senkou_span_a', 'rsi', 'stochastic', 'fib_23.6', 'fib_38.2', 'fib_50.0', 'fib_61.8']].dropna()
    features = data[['macd', 'Volume', 'senkou_span_a', 'rsi', 'stochastic', 'fib_23.6', 'fib_38.2', 'fib_50.0', 'fib_61.8', 'pe_ratio', 'growth_rate']].dropna()

    targets = data['target'].dropna()

    features = features.loc[features.index.intersection(targets.index)]
    targets = targets.loc[targets.index.intersection(features.index)]
    
    return features, targets

def predict_trade_success(symbol, date):
    data = get_realtime_stock_data(symbol)
    if data is None or data.empty:
        return
    
    data = data[data.index <= date]
    
    features, targets = generate_features_and_targets(data)
    
    if features.empty or targets.empty:
        print(f"Not enough data points available for {symbol}.")
        return

    # Check if there are at least two classes in the targets, otherwise skip
    if len(targets.unique()) < 2:
        print(f"Not enough class diversity in the targets for {symbol}. Skipping.")
        return 
       
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    model = LogisticRegression()
    model.fit(features_scaled, targets)
    
    latest_features_scaled = features_scaled[-1].reshape(1, -1)
    success_probability = model.predict_proba(latest_features_scaled)[:, 1][0]
    
    print(f"For {symbol} on {date}:")
    print(f"Probability of Hitting +20% Profit Target: {success_probability:.2f}")
    
    if success_probability > 0.5:
        print("Recommendation: Buy")
    else:
        print("Recommendation: Do Not Buy")
    return symbol, success_probability

def query_buy_decision_for_all_sp500():
    sp500_symbols =  get_sp500_symbols()
    successful_trades = []
    date_str = input("Enter a date (YYYY-MM-DD) to simulate: ")
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        return
    
    for symbol in sp500_symbols:
        print(f"\nProcessing {symbol}...")
        result = predict_trade_success(symbol, date)  
        if result is not None:
            symbol, success_probability = result
        else:
            symbol, success_probability = None, None
            
        if symbol is not None and success_probability is not None:  
             if  success_probability > 0.5:
                successful_trades.append((symbol, success_probability))
                
    successful_trades.sort(key=lambda x: x[1], reverse=True)    
    for symbol, success_probability in successful_trades[:10]:
            print (f"\nBuy trigger for ticker: {symbol}. Probability: {success_probability:.2f}")
    if len(successful_trades) == 0:
        print("\nNo trades with probability of success higher than 50% found.")

pd.set_option('future.no_silent_downcasting', True)
query_buy_decision_for_all_sp500()
