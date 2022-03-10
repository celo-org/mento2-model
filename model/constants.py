"""
Constants used in the model e.g. number of epochs in a year, Gwei in 1 CELO
"""

gwei = 1e9
wei = 1e18
blocktime_seconds = 5
blocks_per_day = 24 * 60 * 60 // blocktime_seconds
blocks_per_month = blocks_per_day * 30
blocks_per_year = blocks_per_month * 12
seconds_per_epoch = blocks_per_day * blocktime_seconds

celo_genesis_supply = 600000000
celo_max_supply = 1000000000
