import os
import requests
import pandas as pd
import pandas_ta as ta
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
if not API_KEY:
    raise ValueError("Missing API key. Please set ALPHA_VANTAGE_API_KEY in your .env file.")

BASE_URL = "https://www.alphavantage.co/query"
app = Flask(__name__)

# Fetch stock data
def fetch_stock_data(symbol):
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": API_KEY,
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if "Time Series (Daily)" not in data:
            raise ValueError(f"No 'Time Series (Daily)' data found for symbol: {symbol}")

        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient="index", dtype=float)
        df.rename(columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume"
        }, inplace=True)
        df.sort_index(inplace=True)
        return df
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error occurred: {e}")
    except ValueError as ve:
        raise ValueError(f"Data error: {ve}")

# Calculate indicators (Bollinger Bands removed)
def calculate_indicators(df):
    if df.empty:
        raise ValueError("No data available to calculate indicators.")

    try:
        indicators = {
            "MA": df["close"].rolling(window=20).mean().iloc[-1],
            "RSI": ta.rsi(df["close"]).iloc[-1],
            "ADX": ta.adx(df["high"], df["low"], df["close"])["ADX_14"].iloc[-1],
            "MACD": ta.macd(df["close"])["MACD_12_26_9"].iloc[-1],
            "OBV": ta.obv(df["close"], df["volume"]).iloc[-1],
            "Stochastic Oscillator": ta.stoch(df["high"], df["low"], df["close"]).iloc[-1].to_dict(),
        }
        return indicators
    except Exception as e:
        raise ValueError(f"Error calculating indicators: {e}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        df = fetch_stock_data(symbol)
        if df is None:
            return jsonify({"error": "Stock data not found"}), 404

        indicators = calculate_indicators(df)
        latest_data = df.iloc[-1].to_dict()

        response = {
            "symbol": symbol.upper(),
            "date": df.index[-1],
            "latest_data": latest_data,
            "indicators": indicators,
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
