from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
import pandas as pd
import numpy as np

# Constants
API_KEY = "MFSNKGMEDOPRMOE5"  # Replace with your actual Alpha Vantage API key
BASE_URL = "https://www.alphavantage.co/query"

# Flask App Initialization
app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Fetch stock data - Basic
def fetch_stock_data(symbol):
    """Fetch stock data from Alpha Vantage API using free endpoint."""
    symbol = symbol.upper()
    params = {
        "function": "TIME_SERIES_DAILY",  # Use free-tier endpoint
        "symbol": symbol,
        "outputsize": "compact",
        "apikey": API_KEY,
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Debug the raw API response
        print(data)

        # Handle common API issues
        if "Note" in data:
            raise ValueError("API limit reached or invalid API key.")
        if "Error Message" in data:
            raise ValueError(f"Invalid stock symbol: {symbol}")
        if "Time Series (Daily)" not in data:
            raise ValueError(f"No 'Time Series (Daily)' data found for symbol: {symbol}")

        # Process the time series data
        time_series = data["Time Series (Daily)"]
        df = pd.DataFrame.from_dict(time_series, orient="index", dtype=float)
        df.rename(columns={
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume"
        }, inplace=True)

        # Handle missing data
        df.replace(["NA", "NaN", "nan"], np.nan, inplace=True)
        df.dropna(inplace=True)

        # Format the response
        latest_date = df.index[0]
        latest_data = df.iloc[0].to_dict()
        time_series_dict = df.head(10).to_dict(orient="index")

        return {
            "symbol": symbol,
            "date": latest_date,
            "latest_data": latest_data,
            "time_series": time_series_dict,
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error occurred: {e}")
    except ValueError as ve:
        raise ValueError(f"Data error: {ve}")

# Fetch sma data
def fetch_sma_data(symbol, interval, time_period):
    """Fetch SMA data from Alpha Vantage API."""
    params = {
        "function": "SMA",
        "symbol": symbol,
        "interval": interval,
        "time_period": time_period,
        "series_type": "close",  # Using closing price for SMA
        "apikey": API_KEY,
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Debug the raw API response
        print(data)

        # Handle common API issues
        if "Note" in data:
            raise ValueError("API limit reached or invalid API key.")
        if "Error Message" in data:
            raise ValueError(f"Invalid stock symbol: {symbol}")
        if "Technical Analysis: SMA" not in data:
            raise ValueError(f"No SMA data found for symbol: {symbol}")

        # Process SMA data
        sma_data = data["Technical Analysis: SMA"]
        processed_data = [{"date": date, "sma": float(values["SMA"])} for date, values in sma_data.items()]

        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "time_period": time_period,
            "sma_data": processed_data[:10],  # Get the latest 10 SMA values
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error occurred: {e}")
    except ValueError as ve:
        raise ValueError(f"Data error: {ve}")



# EMA data

def fetch_ema_data(symbol, interval, time_period, series_type="close"):
    """Fetch EMA data from Alpha Vantage API."""
    params = {
        "function": "EMA",
        "symbol": symbol,
        "interval": interval,
        "time_period": time_period,
        "series_type": series_type,
        "apikey": API_KEY,
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Debug the raw API response
        print(data)

        # Handle common API issues
        if "Note" in data:
            raise ValueError("API limit reached or invalid API key.")
        if "Error Message" in data:
            raise ValueError(f"Invalid stock symbol: {symbol}")
        if "Technical Analysis: EMA" not in data:
            raise ValueError(f"No EMA data found for symbol: {symbol}")

        # Process EMA data
        ema_data = data["Technical Analysis: EMA"]
        processed_data = [{"date": date, "ema": float(values["EMA"])} for date, values in ema_data.items()]

        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "time_period": time_period,
            "series_type": series_type,
            "ema_data": processed_data[:10],  # Get the latest 10 EMA values
        }
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error occurred: {e}")
    except ValueError as ve:
        raise ValueError(f"Data error: {ve}")



# Serve the main HTML page
@app.route('/')
def home():
    return render_template('index.html')


# API Route to fetch stock data
@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    try:
        data = fetch_stock_data(symbol)
        return jsonify(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# API route to fetch SMA data
@app.route('/api/sma/<symbol>', methods=['GET'])
def get_sma_data(symbol):
    try:
        interval = request.args.get("interval", "daily")  # Default to 'daily'
        time_period = int(request.args.get("time_period", 10))  # Default to 10
        data = fetch_sma_data(symbol, interval, time_period)
        return jsonify(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


#APi Route to fetch EMA Data
@app.route('/api/ema/<symbol>', methods=['GET'])
def get_ema_data(symbol):
    try:
        interval = request.args.get("interval", "daily")  # Default to 'daily'
        time_period = int(request.args.get("time_period", 10))  # Default to 10
        series_type = request.args.get("series_type", "close")  # Default to 'close'
        data = fetch_ema_data(symbol, interval, time_period, series_type)
        return jsonify(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400



# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
