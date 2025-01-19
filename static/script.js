document.addEventListener("DOMContentLoaded", () => {
    const fetchButton = document.getElementById("fetch-data");
    const loadingIndicator = document.getElementById("loading");

    fetchButton.addEventListener("click", async () => {
        const symbol = document.getElementById("stock-symbol").value.trim();

        if (!symbol) {
            alert("Please enter a stock ticker.");
            return;
        }

        loadingIndicator.style.display = "block";

        try {
            const response = await fetch(`/api/stock/${symbol}`);
            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Update UI with stock data
            document.getElementById("symbol").innerText = data.symbol;
            document.getElementById("date").innerText = data.date;
            document.getElementById("open").innerText = data.latest_data.open;
            document.getElementById("high").innerText = data.latest_data.high;
            document.getElementById("low").innerText = data.latest_data.low;
            document.getElementById("close").innerText = data.latest_data.close;
            document.getElementById("volume").innerText = data.latest_data.volume;

            // Update Chart
            const times = Object.keys(data.time_series).slice(0, 10).reverse();
            const prices = times.map(time => data.time_series[time].close);

            updateChart(times, prices);
        } catch (error) {
            document.getElementById("error-message").innerText = error.message;
        } finally {
            loadingIndicator.style.display = "none";
        }
    });

    const ctx = document.getElementById("stockChart").getContext("2d");
    const chart = new Chart(ctx, {
        type: "line",
        data: { labels: [], datasets: [{ label: "Stock Price", data: [] }] },
    });

    function updateChart(labels, data) {
        chart.data.labels = labels;
        chart.data.datasets[0].data = data;
        chart.update();
    }
});



// Event listener for SMA data
document.addEventListener("DOMContentLoaded", () => {
    const fetchButton = document.getElementById("fetch-data");
    const loadingIndicator = document.getElementById("loading");

    fetchButton.addEventListener("click", async () => {
        const symbol = document.getElementById("stock-symbol").value.trim();

        if (!symbol) {
            alert("Please enter a stock ticker.");
            return;
        }

        loadingIndicator.style.display = "block";

        try {
            // Fetch SMA data
            const smaResponse = await fetch(`/api/sma/${symbol}?interval=daily&time_period=10`);
            const smaData = await smaResponse.json();

            if (smaData.error) {
                throw new Error(smaData.error);
            }

            // Update UI with SMA data
            const smaList = document.getElementById("sma-data");
            smaList.innerHTML = ""; // Clear previous SMA data
            smaData.sma_data.forEach(item => {
                const listItem = document.createElement("li");
                listItem.textContent = `Date: ${item.date}, SMA: ${item.sma}`;
                smaList.appendChild(listItem);
            });
        } catch (error) {
            document.getElementById("error-message").innerText = error.message;
        } finally {
            loadingIndicator.style.display = "none";
        }
    });
});



// Event listener for EMA
document.addEventListener("DOMContentLoaded", () => {
    const fetchButton = document.getElementById("fetch-data");
    const loadingIndicator = document.getElementById("loading");

    fetchButton.addEventListener("click", async () => {
        const symbol = document.getElementById("stock-symbol").value.trim();

        if (!symbol) {
            alert("Please enter a stock ticker.");
            return;
        }

        loadingIndicator.style.display = "block";

        try {
            // Fetch EMA data
            const emaResponse = await fetch(`/api/ema/${symbol}?interval=daily&time_period=10&series_type=close`);
            const emaData = await emaResponse.json();

            if (emaData.error) {
                throw new Error(emaData.error);
            }

            // Update UI with EMA data
            const emaList = document.getElementById("ema-data");
            emaList.innerHTML = ""; // Clear previous EMA data
            emaData.ema_data.forEach(item => {
                const listItem = document.createElement("li");
                listItem.textContent = `Date: ${item.date}, EMA: ${item.ema}`;
                emaList.appendChild(listItem);
            });
        } catch (error) {
            document.getElementById("error-message").innerText = error.message;
        } finally {
            loadingIndicator.style.display = "none";
        }
    });
});

