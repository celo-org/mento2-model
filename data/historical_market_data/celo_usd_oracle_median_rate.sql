SELECT blockTimestamp,
       blockNumber,
       contract,
       method,
       stableToken,
       CAST(medianRateNumerator AS BIGNUMERIC) / POWER(10, 24) AS oracleMedianRate
FROM `celo-testnet-production.rc1_eksportisto.data`
WHERE 12900000 <= blockNumber
  AND blockNumber <= 13094600
  AND -- (SELECT MAX(blockNumber) - 10 FROM rc1_eksportisto.data) AND
        contract IN ('SortedOracles')
  AND method IN ('MedianRate')
  AND medianRateNumerator IS NOT NULL
  AND stableToken IN ('cUSD')
ORDER BY blockNumber ASC
