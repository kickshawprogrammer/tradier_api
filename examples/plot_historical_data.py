"""
Module example demonstrating how to fetch historical market data using the Tradier API.

This script fetches the market data for a specified symbol and plots it using the
Matplotlib library. It calculates the moving averages for the data and plots those as well.

Usage
-----

    python plot_historical_data.py --symbol <symbol_name>

    For example:

    python plot_historical_data.py --symbol SPY

    This fetches the market data for the SPY ETF and plots it in a new window.

"""

import time
import argparse
from datetime import datetime, timedelta

import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, AutoDateLocator
from mplfinance.original_flavor import candlestick_ohlc
import matplotlib.dates as mdates

from _import_token import API_TOKEN as TRADIER_API_TOKEN
from tradier_api import LiveConfig, TradierApiController, Endpoints

# Constants
DEFAULT_SYMBOL = "SPY"
INTERVAL = "daily"
PRICE_SMA_PERIODS = [50, 100, 200]
VOLUME_SMA_PERIOD = 10
MARGIN = 0.02  # 2% margin for y-axis


def calculate_sma(data: pd.Series, period: int) -> pd.Series:
    """Calculate the Simple Moving Average (SMA) for the given period."""
    return data.rolling(window=period).mean()

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Fetch and plot historical market data using the Tradier API."
    )
    parser.add_argument(
        "--symbol",
        type=str,
        default=DEFAULT_SYMBOL,  # Default symbol if none is provided
        help="The stock symbol to fetch data for (e.g., SPY, AAPL, MSFT). Default: SPY",
    )
    args = parser.parse_args()

    # Validate and use the symbol
    symbol = args.symbol.upper()
    print(f"Fetching data for symbol: {symbol}")

    # Start the timer
    start_time = time.time()

    print("Initializing Tradier API...")
    config = LiveConfig(token=TRADIER_API_TOKEN)
    api_controller = TradierApiController(config)

    # Fetch historical data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365 * 2)  # Approx 2 years for SMA calculations
    print(f"Fetching {symbol} historical data from {start_date.date()} to {end_date.date()}...")

    historical_data = api_controller.make_request(
        endpoint=Endpoints.GET_HISTORICAL_PRICES,
        query_params={
            "symbol": symbol,
            "interval": INTERVAL,
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
        },
    )

    # End the timer and print execution time
    end_time = time.time()
    print(f"Script completed in {end_time - start_time:.3f} seconds.")

    # Convert data to a DataFrame
    print("Processing historical data...")
    data = pd.DataFrame(historical_data["history"]["day"])
    data["date"] = pd.to_datetime(data["date"])
    data.set_index("date", inplace=True)

    # Calculate SMAs for prices
    print("Calculating SMAs for prices...")
    for period in PRICE_SMA_PERIODS:
        data[f"SMA{period}"] = calculate_sma(data["close"], period)

    # Calculate SMA for volume
    print("Calculating SMA for volume...")
    data["VolumeSMA10"] = calculate_sma(data["volume"], VOLUME_SMA_PERIOD)

    # Add column to indicate up/down days for volume color coding
    data["up"] = data["close"] >= data["open"]

    # Trim data to plot the last 200 days
    plot_data = data.iloc[-200:]

    # Prepare data for candlestick plotting
    print("Preparing data for candlesticks...")
    plot_data["date_numeric"] = mdates.date2num(plot_data.index)
    ohlc = plot_data[["date_numeric", "open", "high", "low", "close"]].values

    # Determine y-axis limits for candlestick chart
    max_price = max(
        plot_data["high"].max(),
        plot_data["SMA50"].max(),
        plot_data["SMA100"].max(),
        plot_data["SMA200"].max(),
    )
    min_price = min(
        plot_data["low"].min(),
        plot_data["SMA50"].min(),
        plot_data["SMA100"].min(),
        plot_data["SMA200"].min(),
    )
    price_margin = (max_price - min_price) * MARGIN
    y_min = min_price - price_margin
    y_max = max_price + price_margin

    # Normalize volume for plotting
    max_volume = plot_data["volume"].max()
    volume_scale_factor = max_volume / (8 * 7)  # Scale down by 7/8ths of the chart height
    normalized_volume = plot_data["volume"] / volume_scale_factor
    max_normalized_volume = normalized_volume.max()

    matplotlib.rcParams["toolbar"] = "none"

    # Plot the data
    print("Plotting data...")
    fig, ax_candlestick = plt.subplots(figsize=(7, 4))

    # Plot candlesticks
    candlestick_ohlc(
        ax_candlestick,
        ohlc,
        width=0.6,
        colorup="green",
        colordown="red",
        alpha=0.8,
    )

    ax_candlestick.plot(plot_data.index, plot_data["SMA50"], color="blue", linewidth=1.5, label="SMA50")
    ax_candlestick.plot(plot_data.index, plot_data["SMA100"], color="green", linewidth=1.5, label="SMA100")
    ax_candlestick.plot(plot_data.index, plot_data["SMA200"], color="red", linewidth=1.5, label="SMA200")

    # Add the legend
    ax_candlestick.legend()

    # Set y-axis limits for candlestick chart
    ax_candlestick.set_ylim(y_min, y_max)

    # Add a secondary y-axis for volume bars
    ax_volume = ax_candlestick.twinx()
    ax_volume.set_ylim(0, 8)  # Volume occupies the bottom 1/8th of the chart
    ax_volume.bar(
        plot_data.index,
        normalized_volume / max_normalized_volume,
        color=plot_data["up"].map({True: "green", False: "red"}),
        alpha=0.3,
        width=0.6,
    )
    # Plot Volume SMA on normalized scale
    ax_volume.plot(
        plot_data.index,
        plot_data["VolumeSMA10"] / volume_scale_factor / max(normalized_volume),
        color="orange",
        linewidth=1.5,
        label="VolumeSMA10",
    )
    # ax_volume.legend()

    # Formatting
    ax_candlestick.set_title(f"{symbol} Candlesticks with SMAs and Volume")
    ax_candlestick.set_ylabel("Price")
    ax_candlestick.xaxis.set_major_locator(AutoDateLocator())
    ax_candlestick.xaxis.set_major_formatter(DateFormatter("%b-%d"))
    plt.xticks(rotation=45)

    # Adjust layout to ensure visibility
    plt.tight_layout()

    # Show the plot
    plt.show()


if __name__ == "__main__":
    main()
