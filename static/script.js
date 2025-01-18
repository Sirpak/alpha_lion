const fetchButton = document.getElementById("fetch-data");
const loadingIndicator = document.getElementById("loading");
const apiKey = "MFSNKGMEDOPRMOE5"; // Replace with your actual API key
const baseUrl = "https://www.alphavantage.co/query";

const ctx = document.getElementById("stockChart").getContext("2d");
const chart = new Chart(ctx, {
    type: "line",
    data: {
        labels: [], // Time labels
        datasets: [{
            label: "Stock Price",
            data: [], // Stock prices
            borderColor: "rgba(75, 192, 192, 1)",
            borderWidth: 2,
            fill: false
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: true
            }
        }
    }
});

// Fetch stock data
fetchButton.addEventListener("click", function () {
    const symbol = document.getElementById("stock-symbol").value.trim();

    // Clear previous data or error messages
    document.getElementById("error-message").innerText = "";
    document.getElementById("symbol").innerText = "";
    document.getElementById("date").innerText = "";
    document.getElementById("open").innerText = "";
    document.getElementById("high").innerText = "";
    document.getElementById("low").innerText = "";
    document.getElementById("close").innerText = "";
    document.getElementById("volume").innerText = "";
    document.getElementById("ma").innerText = "";
    document.getElementById("rsi").innerText = "";
    document.getElementById("adx").innerText = "";
    document.getElementById("macd").innerText = "";
    document.getElementById("bollinger").innerText = "";
    document.getElementById("obv").innerText = "";
    document.getElementById("stochastic").innerText = "";

    if (!symbol) {
        document.getElementById("error-message").innerText = "Please enter a stock ticker.";
        return;
    }

    // Show loading indicator
    loadingIndicator.style.display = "block";

    // Fetch stock data from the backend
    fetch(`/api/stock/${symbol}`)
        .then((response) => response.json())
        .then((data) => {
            loadingIndicator.style.display = "none"; // Hide loading indicator

            if (data.error) {
                document.getElementById("error-message").innerText = data.error;
                return;
            }

            // Populate stock data
            document.getElementById("symbol").innerText = data.symbol;
            document.getElementById("date").innerText = data.date;
            document.getElementById("open").innerText = data.latest_data.open.toFixed(2);
            document.getElementById("high").innerText = data.latest_data.high.toFixed(2);
            document.getElementById("low").innerText = data.latest_data.low.toFixed(2);
            document.getElementById("close").innerText = data.latest_data.close.toFixed(2);
            document.getElementById("volume").innerText = data.latest_data.volume;

            // Populate technical indicators
            document.getElementById("ma").innerText = data.indicators.MA.toFixed(2);
            document.getElementById("rsi").innerText = data.indicators.RSI.toFixed(2);
            document.getElementById("adx").innerText = data.indicators.ADX.toFixed(2);
            document.getElementById("macd").innerText = data.indicators.MACD.toFixed(2);
            document.getElementById("bollinger").innerText = JSON.stringify(data.indicators["Bollinger Bands"]);
            document.getElementById("obv").innerText = data.indicators.OBV.toFixed(2);
            document.getElementById("stochastic").innerText = JSON.stringify(data.indicators["Stochastic Oscillator"]);

            // Update chart with the most recent 10 points
            const recentTimes = Object.keys(data.latest_data).slice(0, 10).reverse();
            const recentPrices = recentTimes.map(time => parseFloat(data.latest_data[time]["close"]));
            updateChart(recentTimes, recentPrices);
        })
        .catch((error) => {
            loadingIndicator.style.display = "none"; // Hide loading indicator
            document.getElementById("error-message").innerText = `Error: ${error.message}`;
        });
});

// Update the chart with new data
function updateChart(timeLabels, prices) {
    chart.data.labels = timeLabels;
    chart.data.datasets[0].data = prices;
    chart.update();
}

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

        # Replace string NaNs with actual np.nan and clean data
        df.replace(["NA", "NaN", "nan"], np.nan, inplace=True)
        df = df.astype(float)

        # Handle missing data
        df.dropna(inplace=True)

        df.sort_index(inplace=True)
        return df
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Network error occurred: {e}")
    except ValueError as ve:
        raise ValueError(f"Data error: {ve}")
