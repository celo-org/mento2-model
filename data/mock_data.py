"""
 Creating mock data to test historical simulation
"""
from pathlib import Path
import pandas as pd
import numpy as np

CUSD_USD_VARIANCE_PER_BLOCK = 0.1 / (365 * 24 * 60 *12)
CELO_USD_VARIANCE_PER_BLOCK = 1 / (365 * 24 * 60 *12)
samples = np.random.multivariate_normal(
    [0, 0],
    np.array([
        [CUSD_USD_VARIANCE_PER_BLOCK, 0],
        [0, CELO_USD_VARIANCE_PER_BLOCK]]
    ),
    24 * 60 * 12
    )
temp = pd.DataFrame(samples, columns=('cusd_usd', 'celo_usd'))
temp.index += 1
data_path = Path(__file__, "../mock_logreturns.prq")
temp = temp.to_parquet(data_path.resolve())
#temp = temp.to_parquet('../../data/mock_logreturns.prq')
