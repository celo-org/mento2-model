SELECT
    timestamp,
    exchange,
    ticker,
    mid_price
FROM `celo-testnet-production.cp_doto.market_data`
WHERE
    timestamp >= (SELECT blockTimestamp FROM `celo-testnet-production.rc1_eksportisto.data` WHERE blockNumber = 12900001 LIMIT 1)
  AND timestamp <= (SELECT blockTimestamp FROM `celo-testnet-production.rc1_eksportisto.data` WHERE blockNumber = 13094600 LIMIT 1)
  AND exchange = 'okcoin'
  AND ticker = 'CUSD/USD'
