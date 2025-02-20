import os
import time
import pandas as pd
import multiprocessing
from decimal import Decimal, ROUND_DOWN
from dotenv import load_dotenv
from binance.client import Client

# Load environment variables
load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Initialize Binance client
client = Client(api_key, api_secret)

# Define trading pair
SYMBOL = "BTCUSDT"

# Store last checked order ID to avoid duplicate processing
last_checked_order_id = None

# Function to fetch recent executed orders
def get_recent_executed_orders():
    """Fetch the most recent executed orders for BTCUSDT."""
    orders = client.get_all_orders(symbol=SYMBOL)
    executed_orders = [order for order in orders if order["status"] == "FILLED"]
    
    if executed_orders:
        # Sort orders by execution time (latest first)
        executed_orders.sort(key=lambda x: x["time"], reverse=True)
    
    return executed_orders

# Function to place a sell order at 1% profit
def sell_at_profit(order):
    """Places a sell order at 1% profit from the buy price and waits until it executes."""
    buy_price = float(order["price"])
    quantity = float(order["executedQty"])
    
    # Format quantity to Binance's requirements
    formatted_quantity = Decimal(str(quantity)).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)
    
    sell_price = round(buy_price * 1.03, 2)  # 1% profit target, rounded to 2 decimal places
    
    print(f"Attempting to sell {formatted_quantity} BTC at {sell_price} USDT...")

    while True:
        try:
            # Check if order is already sold
            balances = client.get_asset_balance(asset="BTC")
            available_btc = float(balances["free"])
            
            if available_btc < quantity:
                print("Order already sold or insufficient balance. Exiting process.")
                break
            
            # Place a limit sell order
            sell_order = client.order_limit_sell(
                symbol=SYMBOL,
                quantity=str(formatted_quantity),  # Convert to string for Binance API
                price=str(sell_price)  # Convert to string for Binance API
            )
            print(f"Sell order placed: {sell_order}")
            break  # Exit loop after placing order
            
        except Exception as e:
            print(f"Error placing sell order: {e}")
        
        time.sleep(10)  # Wait 10 seconds before retrying

# Function to monitor and start subprocesses
def monitor_orders():
    global last_checked_order_id

    while True:
        try:
            executed_orders = get_recent_executed_orders()
            if executed_orders:
                latest_order = executed_orders[0]  # Most recent order
                latest_order_id = latest_order["orderId"]

                if latest_order["side"] == "BUY" and latest_order_id != last_checked_order_id:
                    print(f"New BUY order detected: {latest_order}")
                    last_checked_order_id = latest_order_id
                    
                    # Start a new process to sell at profit
                    sell_process = multiprocessing.Process(target=sell_at_profit, args=(latest_order,))
                    sell_process.start()

            else:
                print("No new orders found.")
                
        except Exception as e:
            print(f"Error checking orders: {e}")
        
        time.sleep(60)  # Check for new orders every 60 seconds

# Run the monitoring process
if __name__ == "__main__":
    monitor_orders()
