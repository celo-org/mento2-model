import os
import pandas as pd

# Fetch CSV file relative to current file path
file_celo_price_cap_volume_csv = os.path.join(os.path.dirname(__file__), "celo_price_cap_volume.csv")
file_cusd_price_cap_volume_csv = os.path.join(os.path.dirname(__file__), "cusd_price_cap_volume.csv")

# Get df for historical CELO data
df_celo_price_cap_volume_supply = pd.read_csv(file_celo_price_cap_volume_csv, na_values=[0])
d
df_celo_price_cap_volume_supply = df_celo_price_cap_volume_supply.set_index(['snapped_at'], drop=False)
df_celo_price_cap_volume_supply['supply'] = (
        df_celo_price_cap_volume_supply['market_cap'] / df_celo_price_cap_volume_supply['price']
)

celo_price_mean = df_celo_price_cap_volume_supply['price'].mean()
celo_supply_mean = df_celo_price_cap_volume_supply['supply'].mean()

# Get df for historical cUSD data
df_cusd_price_cap_volume_supply = pd.read_csv(file_cusd_price_cap_volume_csv, na_values=[0])
df_cusd_price_cap_volume_supply = df_cusd_price_cap_volume_supply.set_index(['snapped_at'], drop=False)
df_cusd_price_cap_volume_supply['supply'] = (
        df_cusd_price_cap_volume_supply['market_cap'] / df_cusd_price_cap_volume_supply['price']
)

cusd_price_mean = df_cusd_price_cap_volume_supply['price'].mean()
cusd_supply_mean = df_cusd_price_cap_volume_supply['supply'].mean()
