import os
import json
import pandas as pd
from dotenv import load_dotenv
from binance.client import Client

# Load environment variables
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Initialize Binance client
client = Client(api_key, api_secret)

# Define the symbol to track (BTCUSDT)
SYMBOL = "BTCUSDT"

# Function to fetch all executed orders for BTCUSDT
def get_executed_orders(symbol):
    """Fetches all executed (filled) orders for BTCUSDT."""
    orders = client.get_all_orders(symbol=symbol)
    executed_orders = [order for order in orders if order["status"] == "FILLED"]
    return executed_orders

# Function to track BTCUSDT positions
def track_btc_positions():
    executed_orders = get_executed_orders(SYMBOL)
    btc_positions = []
    
    for order in executed_orders:
        btc_positions.append({
            "orderId": order["orderId"],
            "side": order["side"],
            "price": float(order["price"]),
            "origQty": float(order["origQty"]),
            "executedQty": float(order["executedQty"]),
            "time": pd.to_datetime(order["time"], unit="ms")
        })

    # Convert to DataFrame
    df_positions = pd.DataFrame(btc_positions)

    # Save to CSV
    csv_filename = "btc_executed_orders.csv"
    df_positions.to_csv(csv_filename, index=False)
    
    print(f"BTCUSDT executed orders saved to {csv_filename}")


    return df_positions

# Run the tracking function
track_btc_positions()
