### Historical Values
A rather random historical data time series of CELO and cUSD market cap and volume to
initialize the simulation.

### Mock Data
If no historical data is provided, mock log returns can be generated with mock_data.py.

### Historical Market Data
Real historical data of CELO and cUSD that can be plugged into the simulation.
The data file must include price time series of `CELO`, `cUSD`, `BTC` and `ETH` with column names
`celo_usd`, `cusd_usd`, `btc_usd` and `eth_usd`. The frequency needs to match
`simulation_configuration.BLOCKS_PER_TIMESTEP`.

- Data for CELO and cUSD comes from cLabs internal data
- BTC and ETH data comes from https://www.cryptodatadownload.com/data/ftx/
