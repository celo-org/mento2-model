# Creating mock data to test historical simulation

import pandas as pd
import dask.dataframe as dd
import numpy as np


samples = np.exp(np.random.multivariate_normal(
    [0, 0], np.array([[0.0003, 0], [0, 0.0003]]), 365 * 24 * 60 * 12))
temp = pd.DataFrame(samples, columns=('cusd_usd', 'celo_usd'))
temp.index += 1
temp = temp.to_parquet('data/mock_logreturns.prq')
