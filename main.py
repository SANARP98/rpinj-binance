print("Binance")
from dotenv import load_dotenv
import os 
from binance.client import Client
import pandas as pd

load_dotenv()
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

client = Client(api_key, api_secret)

# Example: Get account info
account_info = client.get_account()
print(account_info)

import json

# Fetch account info
account_info = client.get_account()

# Define the file name
file_name = "account_info.txt"

# Write account info to the file
with open(file_name, "w") as file:
    json.dump(account_info, file, indent=4)

print(f"Account info saved to {file_name}")



import pandas as pd

# Your account_info dictionary (make sure it's properly retrieved from Binance API)
balances = account_info['balances']

# Filter out assets with non-zero free or locked balances
non_zero_balances = [
    balance for balance in balances if float(balance['free']) > 0 or float(balance['locked']) > 0
]

# Convert to DataFrame
df = pd.DataFrame(non_zero_balances)

# Display DataFrame
print(df)
