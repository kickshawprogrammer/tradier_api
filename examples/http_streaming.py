"""
Module example demonstrating how to fetch real-time market events using the Tradier API.

This script will establish a streaming HTTP connection to the Tradier API and stream
market events for the specified symbols.

Please refer to `_import_token.py` for details on how to set up API token values.
"""
from tradier_api import LiveConfig, TradierStreamController, TradierHttpStreamer, SymbolsParams
from _import_token import API_TOKEN as TRADIER_API_TOKEN

def on_open():
    print("WebSocket connection opened.")

def on_message(message):
    print(f"Received message: {message}")

def on_close():
    print("WebSocket connection closed.")

def on_error(error):
    print(f"Error: {error}")

if __name__ == "__main__":
    try:
        # Initialize the API configuration and HTTP stream controller
        config = LiveConfig(token=TRADIER_API_TOKEN)
        streamer = TradierHttpStreamer(
            config=config,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            on_error=on_error
        )

        # Initialize the stream controller
        controller = TradierStreamController(config=config, streamer=streamer)
        params = SymbolsParams(symbols=["AAPL", "TSLA", "SPY"])

        # Start streaming HTTP data for specific symbols
        print("Streaming HTTP data... Press Ctrl+C to stop.")
        controller.start(params)

    except KeyboardInterrupt:
        print("\nStopped streaming.")

    finally:
        # Streaming happens in a separate thread, so close that thread
        controller.close()
