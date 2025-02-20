import os
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

# Function to fetch all executed BTCUSDT orders
def get_executed_orders(symbol):
    """Fetches all executed (filled) orders for BTCUSDT."""
    orders = client.get_all_orders(symbol=symbol)
    executed_orders = [order for order in orders if order["status"] == "FILLED"]
    return executed_orders

# Function to calculate open BTC positions
def calculate_open_btc_position():
    executed_orders = get_executed_orders(SYMBOL)
    print(f"Total executed orders: {len(executed_orders)}")
    print(f"Executed orders: {executed_orders}")
    btc_positions = []

    total_btc_bought = 0
    total_btc_sold = 0

    for order in executed_orders:
        qty = float(order["executedQty"])
        if order["side"] == "BUY":
            total_btc_bought += qty
        elif order["side"] == "SELL":
            total_btc_sold += qty

        btc_positions.append({
            "orderId": order["orderId"],
            "side": order["side"],
            "price": float(order["price"]),
            "origQty": float(order["origQty"]),
            "executedQty": qty,
            "time": pd.to_datetime(order["time"], unit="ms")
        })

    # Open BTC position calculation
    open_btc_position = total_btc_bought - total_btc_sold

    # Convert to DataFrame
    df_positions = pd.DataFrame(btc_positions)

    # Save executed orders to CSV
    csv_filename = "btc_executed_orders.csv"
    df_positions.to_csv(csv_filename, index=False)
    
    print(f"BTCUSDT executed orders saved to {csv_filename}")
    print(f"Total BTC Bought: {total_btc_bought}")
    print(f"Total BTC Sold: {total_btc_sold}")
    print(f"Open BTC Position: {open_btc_position} BTC")


    return open_btc_position

# Run the function to check open BTC positions
open_position = calculate_open_btc_position()
print(f"Your current open BTC position: {open_position} BTC")
