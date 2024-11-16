from tradier_api import LiveConfig, TradierStreamController, TradierHttpStreamer
from _import_token import API_TOKEN as TRADIER_API_TOKEN

def on_message(message):
    print(f"Received message: {message}")


if __name__ == "__main__":
    try:
    # Initialize the API configuration and HTTP stream controller
        config = LiveConfig(token=TRADIER_API_TOKEN)
        streamer = TradierHttpStreamer(config=config, on_message=on_message)

        # Initialize the stream controller
        controller = TradierStreamController(config=config, streamer=streamer)
        
        # Start streaming HTTP data for specific symbols
        print("Streaming HTTP data... Press Ctrl+C to stop.")
        controller.start(symbols=["AAPL", "TSLA", "SPY"])    
    except KeyboardInterrupt:
        print("\nStopped streaming.")

    finally:
        controller.close()
