"""
Historical cUSD/cEUR/cREAL price and volume data
"""
import os

import numpy as np
import pandas as pd

def create_dataframes(input_data: str):
    data_csv = os.path.join(os.path.dirname(__file__), input_data)
    data = pd.read_csv(data_csv, na_values=[0])
    data = data.set_index(['snapped_at'], drop=False)
    data['supply'] = (
        data['market_cap'] / data['price']
    )
    return data


# Get df for historical data for CELO and cUSD
DF_CELO_PRICE_CAP_VOLUME_SUPPLY = create_dataframes(
    input_data="celo_price_cap_volume.csv")
DF_CUSD_PRICE_CAP_VOLUME_SUPPLY = create_dataframes(
    input_data="cusd_price_cap_volume.csv")
DF_CEUR_PRICE_CAP_VOLUME_SUPPLY = create_dataframes(
    input_data="cusd_price_cap_volume.csv")
DF_CREAL_PRICE_CAP_VOLUME_SUPPLY = create_dataframes(
    input_data="cusd_price_cap_volume.csv")

CELO_PRICE_MEAN = DF_CELO_PRICE_CAP_VOLUME_SUPPLY['price'].mean()
CELO_SUPPLY_MEAN = DF_CELO_PRICE_CAP_VOLUME_SUPPLY['supply'].mean()
CUSD_PRICE_MEAN = DF_CUSD_PRICE_CAP_VOLUME_SUPPLY['price'].mean()
CUSD_SUPPLY_MEAN = DF_CUSD_PRICE_CAP_VOLUME_SUPPLY['supply'].mean()
CEUR_PRICE_MEAN = DF_CEUR_PRICE_CAP_VOLUME_SUPPLY['price'].mean()
CEUR_SUPPLY_MEAN = DF_CEUR_PRICE_CAP_VOLUME_SUPPLY['supply'].mean()
CREAL_PRICE_MEAN = DF_CREAL_PRICE_CAP_VOLUME_SUPPLY['price'].mean()
CREAL_SUPPLY_MEAN = DF_CREAL_PRICE_CAP_VOLUME_SUPPLY['supply'].mean()

DF_CUSD_PRICE_CAP_VOLUME_SUPPLY['return'] = DF_CUSD_PRICE_CAP_VOLUME_SUPPLY['price'].pct_change()
CUSD_SUPPLY_RETURNS_VOLA_DAILY = DF_CUSD_PRICE_CAP_VOLUME_SUPPLY['return'] .std()
CUSD_SUPPLY_RETURNS_VOLA_ANNUALLY = CUSD_SUPPLY_RETURNS_VOLA_DAILY * np.sqrt(365)
