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
SYMBOL = "TRUMPUSDT"

# Store last checked order ID to avoid duplicate processing
last_checked_order_id = None

# Function to fetch Binance tick size and step size for price & quantity
def get_symbol_filters(symbol):
    """Fetch tick size (price precision) and step size (quantity precision) for a trading pair."""
    exchange_info = client.get_exchange_info()
    for symbol_info in exchange_info["symbols"]:
        if symbol_info["symbol"] == symbol:
            tick_size = Decimal('0.01')  # Default for 2 decimal places
            step_size = Decimal('0.000001')  # Default for Binance's lot size

            for f in symbol_info["filters"]:
                if f["filterType"] == "PRICE_FILTER":
                    tick_size = Decimal(f["tickSize"])  # Price precision (rounding)
                if f["filterType"] == "LOT_SIZE":
                    step_size = Decimal(f["stepSize"])  # Quantity precision

            return tick_size, step_size
    return Decimal('0.01'), Decimal('0.000001')  # Default values

# Function to fetch recent executed orders
def get_recent_executed_orders():
    """Fetch the most recent executed orders for TRUMPUSDT."""
    orders = client.get_all_orders(symbol=SYMBOL)
    executed_orders = [order for order in orders if order["status"] == "FILLED"]

    if executed_orders:
        # Sort orders by execution time (latest first)
        executed_orders.sort(key=lambda x: x["time"], reverse=True)

    return executed_orders

# Function to place a sell order at 3% profit
def sell_at_profit(order):
    """Places a sell order at 3% profit with correct rounding."""
    buy_price = Decimal(order["price"])
    quantity = Decimal(order["executedQty"])

    # Get correct tick size and step size for TRUMPUSDT
    tick_size, step_size = get_symbol_filters(SYMBOL)

    # Format quantity and price correctly
    formatted_quantity = quantity.quantize(step_size, rounding=ROUND_DOWN)
    sell_price = (buy_price * Decimal('1.03')).quantize(Decimal('0.01'), rounding=ROUND_DOWN)  # Ensure 2 decimal places

    print(f"Attempting to sell {formatted_quantity} TRUMP at {sell_price} USDT...")

    while True:
        try:
            # Check if order is already sold
            balances = client.get_asset_balance(asset="TRUMP")
            available_trump = Decimal(balances["free"])
            
            if available_trump < quantity:
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
