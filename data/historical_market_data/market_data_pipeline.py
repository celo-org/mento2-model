"""
Pipelines bigquery SQL output to market data frame
"""
from pathlib import Path
import pandas as pd

DATA_FOLDER = Path(__file__, "../../../data/historical_market_data/").resolve()
CUSD_FILE_NAME = "cusd_usd_block_12900000_13094600.csv"
CELO_FILE_NAME = "oracle_median_rate_block_12900000_13094600.csv"
TEN_EPOCHS = 17280*10+1 # +1 because it will lose one timestep due to log return calculation later

celo_path = Path(DATA_FOLDER, CELO_FILE_NAME)
oracle_median_rate = pd.read_csv(celo_path)
oracle_median_rate = oracle_median_rate.rename(columns={'oracleMedianRate': 'celo_usd'})
oracle_median_rate = oracle_median_rate[0:TEN_EPOCHS]

cusd_path = Path(DATA_FOLDER, CUSD_FILE_NAME)
cusd_usd = pd.read_csv(cusd_path)
cusd_usd = cusd_usd.rename(columns={'mid_price': 'cusd_usd'})
cusd_usd['timestamp'] = pd.to_datetime(cusd_usd['timestamp'])
cusd_usd = cusd_usd.set_index('timestamp')
cusd_usd = cusd_usd.resample('5S').ffill().dropna()
cusd_usd = cusd_usd[0:TEN_EPOCHS]

historical_market_data = pd.concat([oracle_median_rate['celo_usd'].reset_index(drop=True),
                                    cusd_usd['cusd_usd'].reset_index(drop=True)], axis=1)
historical_market_data.to_csv(Path(DATA_FOLDER, 'cusd_celo_example.csv'), index=False)
