"""
 Creating mock data to test historical simulation
"""
import pandas as pd
import numpy as np

CUSD_USD_VARIANCE_PER_BLOCK = 0.1 / (365 * 24 * 60 * 12)
CELO_USD_VARIANCE_PER_BLOCK = 1 / (365 * 24 * 60 * 12)
samples = np.random.multivariate_normal(
    [0, 0],
    np.array([
        [CUSD_USD_VARIANCE_PER_BLOCK, 0],
        [0, CELO_USD_VARIANCE_PER_BLOCK]]
    ),
    24 * 60 * 12 + 1
)
# mock data single depeg event
#samples = np.array([[0.05, 0] if x == 0 else [0, 0] for x in range(0, 125)])

temp = pd.DataFrame(samples, columns=('cusd_usd', 'celo_usd'))
temp.to_parquet('data/mock_logreturns.prq')
