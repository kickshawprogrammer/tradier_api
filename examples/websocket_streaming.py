from tradier_api import LiveConfig, TradierStreamController,TradierWebsocketStreamer
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
        # Initialize the API configuration and WebSocket streamer
        config = LiveConfig(token=TRADIER_API_TOKEN)
        streamer = TradierWebsocketStreamer(
            config=config,
            on_open=on_open,
            on_message=on_message,
            on_close=on_close,
            on_error=on_error
        )

        # Initialize the stream controller
        controller = TradierStreamController(config=config, streamer=streamer)

        # Start streaming data for specific symbols
        controller.start(symbols=["AAPL", "TSLA", "SPY"])
        print("Streaming WebSocket data... Press Ctrl+C to stop.")
    except KeyboardInterrupt:
        print("\nStopped streaming.")

    finally:
        controller.close()
