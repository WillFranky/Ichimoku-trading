#import time
import traceback
from openpyxl import load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows
#import openpyxl
import pandas as pd
#from pandas import DataFrame
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from plyer import notification
from datetime import datetime, timedelta
import numpy as np 
from sklearn.cluster import KMeans
from scipy.signal import argrelextrema
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from zipfile import BadZipFile
from pandas.tseries.offsets import DateOffset
from datetime import datetime, timedelta
from scipy.interpolate import interp1d



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
    
    # OMXS30
    url = 'https://en.wikipedia.org/wiki/OMX_Stockholm_30'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'class': 'wikitable sortable'})
    for row in table.find_all('tr')[1:]:
        symbol = row.find_all('td')[1].text.strip()
        #symbols.append(symbol)
   
    
    # RAW MATERIALS
    silver_ticker = 'SLV' #iShares Silver Trust ETF
    gold_ticker = 'GLD' #SPDR Gold Shares ETF
    oil_ticker = 'USO' #United States Oil Fund ETF
    natural_gas_ticker = 'UNG' #United States Natural Gas Fund ETF
    copper_ticker = 'JJC' #iPath Series B Bloomberg Copper Subindex Total Return ETN
    essential_metals_ticker = 'DBB' #Invesco DB Base Metals Fund ETF
    
    symbols.extend([silver_ticker, gold_ticker, oil_ticker, natural_gas_ticker, copper_ticker, essential_metals_ticker])
    
    return symbols
    

def send_notification(message):

    notification.notify(
        title='Bullish Signal Detected',
        message=message,
        timeout=10  
    )

def get_stock_data(symbol, date):
    try:
        start_date=date - timedelta(days=365*3)                
        end_date=date 
    
        stock = yf.Ticker(symbol)
        hist_data = stock.history(start=start_date, end=date)
        
        if hist_data.empty:
            print(f"No data available for symbol {symbol}")
            return None

        # Clean data - complete missing dates and add interpolated values
        
        # Remove timezone information and normalize to midnight
        hist_data.index = hist_data.index.tz_localize(None)
     
         # Create a complete date range and reindex the DataFrame to include all dates
        all_days = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Interpolate values for each column using scipy's interp1d function
        columns_to_interpolate = ['Open', 'High', 'Low', 'Close']
        interpolated_data = pd.DataFrame(index=all_days)
        
        for column in columns_to_interpolate:
            interp_func = interp1d(hist_data.index.astype(int), hist_data[column], kind='linear', fill_value='extrapolate')
            interpolated_values = interp_func(all_days.astype(int))
            interpolated_data[column] = interpolated_values
        
        # Ensure there are no missing values after interpolation
            if interpolated_data.isnull().any().any():
                print("Warning: There are still missing values after interpolation.")
        
        # Return the interpolated historical price data
        hist_data = interpolated_data
               
        hist_data['High'] = hist_data['High'].shift(1)  # Shift the data by one day to avoid look-ahead bias
        hist_data['Low'] = hist_data['Low'].shift(1)  # Shift the data by one day to avoid look-ahead bias  

        stock_info = stock.info
        stock_name = stock_info.get("longName", "Name not found")

        if stock_name == "Name not found":
            print(f"No long name found for {symbol}")
    
        if hist_data is None:
            return ("DefaultName", None)
        else:
            return stock_name, hist_data
                        
    except Exception as e:
        print(f"Error calculating Senkou Span for {symbol}: {e}")
        traceback.print_exc()  # Print the traceback
        return None
        
def calculate_senkou_span(symbol, stock_name, hist_data, date):                                                          
    try:
               
        # Check if there is sufficient data: 52 days required + 26 days for the lagging span +1 for excluding last day in calculations
        if hist_data.shape[0] < 79:
            print(f"Insufficient data for {symbol}. Only {hist_data.shape[0]} days of data available.")
            return None

        # Calculate the highest high and lowest low over the past 26 periods
        high_9 = hist_data['High'].rolling(window=9).max()
        low_9 = hist_data['Low'].rolling(window=9).min()
        tenkan_sen = (high_9 + low_9) / 2
        
        high_26 = hist_data['High'].rolling(window=26).max()
        low_26 = hist_data['Low'].rolling(window=26).min()
        kijun_sen = (high_26 + low_26) / 2
        
        high_52 = hist_data['High'].rolling(window=52).max()
        low_52 = hist_data['Low'].rolling(window=52).min()
        
        # Check if all values are NaN, then skip to avoid error
        if high_52.isnull().all() or low_52.isnull().all():
            print(f"All values in high_52 are NaN for {symbol}")
            return None

        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(periods=26)
       
        # Shift high_52 and low_52
        high_52_shifted = high_52.shift(periods=26)
        low_52_shifted = low_52.shift(periods=26)
     
        # Check if all values in high_52_shifted and low_52_shifted are NaN
        if high_52_shifted.isnull().all():
            print(f"All values in high_52_shifted are NaN for {symbol}")
            return None, None, None, None

        if low_52_shifted.isnull().all():
            print(f"All values in low_52_shifted are NaN for {symbol}")
            return None, None, None, None

        # Fill NaN values in high_52_shifted and low_52_shifted
        first_valid_index_high_shifted = high_52_shifted.first_valid_index()
        first_valid_index_low_shifted = low_52_shifted.first_valid_index()

        if first_valid_index_high_shifted is not None:
            high_52_shifted.fillna(high_52_shifted[first_valid_index_high_shifted], inplace=True)

        if first_valid_index_low_shifted is not None:
            low_52_shifted.fillna(low_52_shifted[first_valid_index_low_shifted], inplace=True)
        
        # Calculate senkou_span_b
        senkou_span_b = ((high_52_shifted + low_52_shifted) / 2)
        tenkan_sen = tenkan_sen.shift(periods=26)
        kijun_sen = kijun_sen.shift(periods=26)
        chikou_span = hist_data['Close'].shift(periods=-26)  # Shifted 26 days into the past

        # Set the option to display all rows
        pd.set_option('display.max_rows', None)

        return senkou_span_a, senkou_span_b, tenkan_sen, kijun_sen, chikou_span

    except Exception as e:
        print(f"Error calculating Senkou Span for {symbol}: {e}")
        traceback.print_exc()  # Print the traceback
        return None
    

def get_resistance_levels(stock_data, symbol):
    # Identify local maxima
    peaks, _ = find_peaks(stock_data['Close'].values)
    maxima_prices = stock_data['Close'].values[peaks]
    maxima_times = np.linspace(0, 1, len(stock_data))[peaks]

    if maxima_prices.size == 0:
            print(f"No maxima found for {symbol}")
            return None
        
    # Get the highest local maxima
    highest_maxima = maxima_prices.max()

    # Prepare data for clustering: Normalize time and price to have similar scales
    X_time = np.linspace(0, 1, len(stock_data)).reshape(-1, 1)
    X_price = (stock_data['Close'].values - np.min(stock_data['Close'])) / (np.max(stock_data['Close']) - np.min(stock_data['Close']))
    
    # Combine time and price data
    X_cluster = np.column_stack((X_time, X_price))
    
    # Add maxima to the clustering data
    maxima_normalized = (maxima_prices - np.min(stock_data['Close'])) / (np.max(stock_data['Close']) - np.min(stock_data['Close']))
    maxima_data = np.column_stack((maxima_times, maxima_normalized))
    X_cluster = np.vstack((X_cluster, maxima_data))

    # Applying KMeans clustering
    num_clusters = 5
    kmeans = KMeans(n_clusters=num_clusters)
    kmeans.fit(X_cluster)

    # Extract cluster centers and rescale back to original price range
    cluster_centers = kmeans.cluster_centers_[:, 1] * (np.max(stock_data['Close']) - np.min(stock_data['Close'])) + np.min(stock_data['Close'])

    # Filter cluster centers to only include those above the current stock price
    current_price = stock_data['Close'].values[-1]
    resistance_levels = cluster_centers[cluster_centers > current_price * 0.9]

    # Add the highest maxima to the resistance levels if it is above the current price
    if highest_maxima > current_price:
        resistance_levels = np.append(resistance_levels, highest_maxima)
        resistance_levels = np.unique(resistance_levels)  # Ensure unique values
   
    return resistance_levels
    

def trading_strategy(sp500_symbols, start_date, end_date):
    try:
        kumo_breakout_detected = False
        triggered_symbols = []
       
        for symbol in sp500_symbols:
            margin_down = 0
            margin_up = 0
           
            result = get_stock_data(symbol, start_date)
            if isinstance(result, (list, tuple)) and len(result) == 2:
                stock_name, stock_data = result
            else:
                print(f"Error fetching data for {symbol}, skipping.")
                continue
            
            price = stock_data['Close'].values[-1]
            resistance_level = get_resistance_levels(stock_data, symbol)
            date=start_date - DateOffset(days=1)            # Using previous days for senkou span because it should be compared to previous days close
            senkou_spans = calculate_senkou_span(symbol, stock_name, stock_data, date)
            date_chikou  = date - DateOffset(days=26)
            
            price_at_chikou = stock_data['Close'].values[-28]  # Get the price 26 days back to be compared with Chiku Span
            
            # Check if senkou_spans is None before unpacking to prevent error
            if senkou_spans is None:                                                    
                print(f"Insufficient data to calculate Senkou Span for {symbol}, skipping.")
                continue
            
            senkou_span_a, senkou_span_b, tenkan_sen, kijun_sen, chikou_span = senkou_spans
            
            senkou_span_a_value = senkou_span_a.get(date.strftime('%Y-%m-%d'))
            senkou_span_a_value = senkou_span_a_value.values[0]
            senkou_span_b_value = senkou_span_b.get(date.strftime('%Y-%m-%d'))
            senkou_span_b_value = senkou_span_b_value.values[0]
            chikou_span_value = chikou_span.get(date_chikou.strftime('%Y-%m-%d'))  
            chikou_span_value = chikou_span_value.values[0]
    
            if resistance_level is not None and resistance_level.size > 0:
    
                resistance_above_price = [level for level in resistance_level if level > price]

                if resistance_above_price:
                    nearest_resistance = sorted(resistance_above_price)[0]
                    if price != 0:
                        margin_up = round(100 * (nearest_resistance - price) / price, 2)
                    else:
                        print("Price is zero, cannot calculate margin_up")
            
            if senkou_span_a_value is not None:
                margin_down = round(100*(price - senkou_span_a_value) / price, 2)
            else:
                print(f"No value found in senkou_span_a for date {date.strftime('%Y-%m-%d')}")
                margin_down = 0  
            
            if senkou_span_a_value is not None and senkou_span_b_value is not None and price:         # not neeeded
                
                if(price > senkou_span_a_value):

                    if (senkou_span_a_value > senkou_span_b_value):
                        
                        if(chikou_span_value > price_at_chikou):
                            print()
                            print("SPAN > PRICE for ", symbol)
                            print(f"Price: {price}")
                            print(f"Nearest resistance: {nearest_resistance}")
                            print(f"Senkou Span A: {senkou_span_a_value}")
                            print(f"Date at Chikou: {date_chikou.strftime('%Y-%m-%d')}")
                            print(f"Price at Chikou: {price_at_chikou}")
                            print(f"Chikou Span: {chikou_span_value}")
                            print()
                        
                            if (price > nearest_resistance or price < nearest_resistance): #0.9 * nearest_resistance):
                                kumo_breakout_detected = True
                                message = f"Kumo breakout detected for {symbol} - Bullish signal! Consider buying."
                                print(message)
                                send_notification(message)
                                triggered_symbols.append(symbol)
                                log_long_trade(stock_name, symbol, stock_data, senkou_span_a_value, senkou_span_b_value, margin_down, margin_up, start_date, end_date)
                                #plot_resistances(stock_data, symbol, resistance_level, senkou_span_a, senkou_span_b, chikou_span, margin_up, margin_down)
                            
                            else:  
                                print(f"Ticker {symbol}, no trigger")
                        else:
                            print(f"Chikou Span below price for {symbol}")
                    else:
                        print(f"Senkou Span A below Senkou Span B for {symbol}")
                else:
                    print()
                    print("SPAN < PRICE for ", symbol)
                    print(f"Price: {price}")
                    print(f"Nearest resistance: {nearest_resistance}")
                    print(f"Senkou Span A: {senkou_span_a_value}")
                    print(f"Date at Chikou: {date_chikou.strftime('%Y-%m-%d')}")
                    print(f"Price at Chikou: {price_at_chikou}")
                    print(f"Chikou Span: {chikou_span_value}")
                    print()
              
        return kumo_breakout_detected, triggered_symbols, start_date
    except Exception as e:
        print(f"An error occurred: {e}")
        
        return False, [], start_date

    return False, [], start_date


def plot_resistances(stock_data, symbol, resistance_levels, senkou_span_a, senkou_span_b, chikou_span, margin_up, margin_down):   
    
    # Calculate the number of values to trim
    trim_values = len(senkou_span_a) - len(stock_data.index)

    # Ensure all spans are aligned with stock_data
    min_len = min(len(stock_data), len(senkou_span_a), len(senkou_span_b), len(chikou_span))

    stock_data = stock_data.iloc[-min_len:]
    senkou_span_a = senkou_span_a.iloc[-min_len:]
    senkou_span_b = senkou_span_b.iloc[-min_len:]
    chikou_span = chikou_span.iloc[-min_len:]
    
    # Plotting
    if resistance_levels is None:
        resistance_levels = []  
    plt.figure(figsize=(28,7))
    plt.plot(stock_data['Close'], label="Close Price")
    
    plt.plot(stock_data.index, senkou_span_a, label="Senkou Span A", color='g')
    plt.plot(stock_data.index, senkou_span_b, label="Senkou Span B", color='r')
    plt.plot(stock_data.index, chikou_span, label="Chikou Span", color='tab:brown')
    
    for level in resistance_levels:
        plt.axhline(y=level, color='r', linestyle='--')
        plt.annotate(f"{level:.2f}", xy=(stock_data.index[-1], level * 1.01), xytext=(0,5), textcoords="offset points", fontsize=15, ha='left', va='center', color='r')
        
    # Fill the area between senkou_span_a and senkou_span_b
    plt.fill_between(stock_data.index, senkou_span_a, senkou_span_b, where=(senkou_span_a > senkou_span_b), color='g', alpha=0.5)
    plt.fill_between(stock_data.index, senkou_span_a, senkou_span_b, where=(senkou_span_a <= senkou_span_b), color='r', alpha=0.5)

    current_price = stock_data['Close'].values[-1]
    
    # Annotation and vertical line for Margin up
    if margin_up != 0:
        margin_up_price = current_price * (1 + margin_up / 100)
        plt.vlines(x=stock_data.index[-1], ymin=current_price, ymax=margin_up_price, color='y', linestyle='--', label="Margin to resistance")
        plt.annotate(f"{margin_up}%", xy=(stock_data.index[-1], margin_up_price), xytext=(-40, -20), textcoords="offset points", fontsize=15, ha='right', va='center', color='y')
    
    # Annotation and vertical line for Margin down
    if margin_down != 0:
        margin_down_price = current_price * (1 - margin_down / 100)
        plt.vlines(x=stock_data.index[-1], ymin=current_price, ymax=margin_down_price, color='m', linestyle='--', label="Margin to span")
        plt.annotate(f"{margin_down}%", xy=(stock_data.index[-1], margin_down_price), xytext=(-40, -20), textcoords="offset points", fontsize=15, ha='right', va='center', color='m')
            
    
    # Identify local maxima and minima
    maxima_indices = argrelextrema(stock_data['Close'].values, np.greater)[0]
    minima_indices = argrelextrema(stock_data['Close'].values, np.less)[0]
    maxima = stock_data['Close'].values[maxima_indices]
    minima = stock_data['Close'].values[minima_indices]
    maxima_times = stock_data.index[maxima_indices].astype(np.int64) // 10**9  # Convert datetime

    plt.title(f'{symbol} Price Data with Ichimoku indicators and KMeans Clustering for resistance levels')
    plt.legend()
    plt.show()
        
    return 

# --------------- PRINT TO EXCEL --------------- #


def create_trades_workbook():
    # Check if the file "long trades.xlsx" exists
    try:
        df = pd.read_excel("long triggers.xlsx", sheet_name='Triggers', engine='openpyxl')
    except FileNotFoundError:
        # If the file does not exist, create it
        with pd.ExcelWriter("long triggers.xlsx") as writer:
            # Create triggers sheet
            triggers_data = {
                'Date': [],
                'Name': [],
                'Ticker': [],
                'Price': [],
                'Price Senkou Span A': [],
                'Senkou Span B': [],
                'Margin to Cloud Span A': [],
                'Margin to resistance': []
            }
            
            triggers_df = pd.DataFrame(triggers_data)
            triggers_df.to_excel(writer, sheet_name='Triggers', index=False)

        print("long triggers.xlsx created successfully.")
        
    except BadZipFile:
        # Handle bad zip file error
        print("File is not a zip file. Please check the file and try again.")
    else:
        print("Excel file 'long triggers.xlsx' already exists.")


def log_long_trade(name, ticker, stock_data, price_senkou_span_a_value, senkou_span_b_value, margin_from_cloud_span_a, margin_to_resistance, start_date, end_date):

    xlsx = load_workbook("long triggers.xlsx")
    ws_triggers = xlsx["Triggers"]
    

    new_row_trigger = pd.DataFrame({
        'Date': [start_date],
        'Name': [name],
        'Ticker': [ticker],
        'Price': [stock_data['Close'].values[-1]], #[get_current_price(ticker, start_date, end_date)],  # Get the current price of the stock
        'Price Senkou Span A': [price_senkou_span_a_value],
        'Senkou Span B': [senkou_span_b_value],
        'Margin from Cloud Span A': [margin_from_cloud_span_a],
        'Margin to resistance': [margin_to_resistance]
    })    
   
    for r in dataframe_to_rows(new_row_trigger, index=False, header=False):  #No index and don't append the column headers
        ws_triggers.append(r) 

    xlsx.save("long triggers.xlsx")
    
    xlsx.close()                   
    
def main():
    
    create_trades_workbook()    
    start_date = datetime.now() - timedelta(3*365)
    start_date_unix = int(start_date.timestamp())
    end_date = datetime.now()
    end_date_unix = int(end_date.timestamp())
    date = end_date - timedelta(days=1)     # Using previous days close  
    
    sp500_symbols = get_sp500_symbols()
    while date < end_date:
        kumo_breakout_detected, triggered_symbols, start_date = trading_strategy(sp500_symbols, date, end_date)

        if not kumo_breakout_detected:
            message = "No Kumo breakout triggers were found for any stock in the S&P 500 index."
            print(message)
        date = date + timedelta(days=1)   

    print()
    print("Done")
        
if __name__ == "__main__":
    main()
