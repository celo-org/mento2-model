import os

import numpy as np
import pandas as pd


def create_dataframes(input_data: str):
    data_csv = os.path.join(os.path.dirname(__file__), input_data)
    df = pd.read_csv(data_csv, na_values=[0])
    df = df.set_index(['snapped_at'], drop=False)
    df['supply'] = (
            df['market_cap'] / df['price']
    )
    return df


# Get df for historical data for CELO and cUSD
df_celo_price_cap_volume_supply = create_dataframes(input_data="celo_price_cap_volume.csv")
df_cusd_price_cap_volume_supply = create_dataframes(input_data="cusd_price_cap_volume.csv")

print(df_cusd_price_cap_volume_supply)

celo_price_mean = df_celo_price_cap_volume_supply['price'].mean()
celo_supply_mean = df_celo_price_cap_volume_supply['supply'].mean()
cusd_price_mean = df_cusd_price_cap_volume_supply['price'].mean()
cusd_supply_mean = df_cusd_price_cap_volume_supply['supply'].mean()

df_cusd_price_cap_volume_supply['return'] = df_cusd_price_cap_volume_supply['price'].pct_change()
cusd_supply_returns_vola_daily = df_cusd_price_cap_volume_supply['return'] .std()
cusd_supply_returns_vola_annually = cusd_supply_returns_vola_daily * np.sqrt(365)
