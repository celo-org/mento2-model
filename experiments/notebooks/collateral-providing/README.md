# Collateral Providing

[Colab Notebook with first simulation](https://colab.research.google.com/drive/1CvZ2FN7gV5SNstNjRk4knyc6SzycrCF5?usp=sharing)

Main idea: Allow users to earn rewards by committing collateral to the reserve.

An illustration of the mechanics of collateral providing:

- Assume the core reserve holds 90M CELO and assume the first collateral provider (CP#1) commits 10M additional CELO to the reserve, then CP#1 receives 10M CP (collateral provider) tokens.
- During a contraction, 10% of the inflowing cStables flow into CP#1s position and 10% of the outflowing CELOs flow out of CP#1s position.
- During expansions, cStables flow out of CP#1s position unless there are no cStables left in the position, at which point they get minted by the reserve and position of CP#1 remains untouched.
- To keep CP-tokens fungible, additional CPs have to provide capital in the same proportion as the current CPs positions, for example 20% of the position value in cUSD and 80% in CELO.
- That means that if another CP, let’s call her CP#2, is providing collateral, this collateral must be provided in the same proportion as the current position of CP#1.
- CP#1 gets incentivized to participate by
- Receiving mento trading fees (spread) on pro-rata basis
- Receiving collateral provision incentives:
- CP-tokens can be locked up for extended periods of time (1M, 3M, 6M, 1Y, 5Y, 10Y) which leads to the CP receiving rewards from Mento.
- The incentivized long lockup periods for CP-tokens lead to protocol owned collateral beyond the original reserve collateral
- Sources of collateral provision rewards: Yield of staked collateral, excess collateral, Mento token

Properties of collateral providing:

- As long as cStables are pegged, neither expansions nor contractions change the value of a CP position. During contractions for example, X USD worth of cStables are flowing in and X USD of CELO is flowing out  - which amounts to value neutrality. This value neutrality is intuitive as the value of debt created equals the additional asset value deposited.
- The risk that CPs take is mainly a cStables price risk - if there are more contractions than expansions, a CP ends up with more cStables than she started out with and if those cStables are trading below a price of one, the CP makes a loss.
- Additionally, CPs take a relative price change risk. However, in contrast to a liquidity provider setup in which relative price changes always lead to impermanent loss, relative price changes of cStables and CELO in the collateral provider setup can also lead to an “impermanent gain” compared to a buy and hold portfolio.
- The collateral provider mechanism is a generalization of the Mento1.0 setup; If no one becomes a CP, we are back to a single-reserve actor setup

Collateral providing - what it achieves:

- It allows to attract additional collateral today to be well prepared for tomorrow (intertemporal value transfer)
- It allows to lock in additional collateral that would otherwise likely be withdrawn during future bad reserve states (good-to-bad state value transfer)
- It helps with absorbing cStables demand shocks as part of the contraction amounts end up with CPs
- It helps with long-term overcollateralization as it incentives the provision of additional reserve collateral
- It transfers cStables to CPs in the worst-case scenario of a permanent depeg (transfer from risk-averse user group to risk-seeking user group who signed up for that risk).
- Creates innovative new earning opportunities for defi users and thereby fosters engagement and growth. CPs rewards can be expected to be sustainable income as they are a compensation for solving an actual problem - taking worst-case scenario risk.
