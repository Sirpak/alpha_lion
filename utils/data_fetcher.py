import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("MFSNKGMEDOPRMOE5")  # Ensure you have this key in your .env file
BASE_URL = "https://www.alphavantage.co/query"

def get_stock_data_from_source(symbol):
    """
    Fetch stock data for a given symbol using Alpha Vantage API.
    :param symbol: Stock ticker symbol (e.g., AAPL, MSFT, BAC)
    :return: Stock data as a dictionary, or None if not found
    """
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "apikey": API_KEY,
    }

    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        # Debug: Print the response for troubleshooting
        print(f"API Response: {data}")

        # Check if the response contains an error
        if "Error Message" in data:
            print(f"API Error: {data['Error Message']}")
            return None

        # Extract the "Time Series (5min)"
        time_series = data.get("Time Series (5min)")
        if not time_series:
            print("No time series data available.")
            return None

        # Get the latest timestamp and its data
        latest_timestamp = max(time_series.keys())
        latest_data = time_series[latest_timestamp]

        # Prepare the result
        return {
            "symbol": symbol,
            "date": latest_timestamp,
            "open": float(latest_data["1. open"]),
            "high": float(latest_data["2. high"]),
            "low": float(latest_data["3. low"]),
            "close": float(latest_data["4. close"]),
            "volume": int(latest_data["5. volume"]),
        }
    except Exception as e:
        print(f"Error fetching stock data for {symbol}: {e}")
        return None

