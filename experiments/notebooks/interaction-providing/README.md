# Interaction farming

**Main idea**: Allow users to earn by committing funds to a contract that guarantees healthy, on-chain protocol interactions at any time.

**Context**: During crisis times, one cannot rely on profit opportunities to be taken even if they are present. This is critical since even if the correct incentives are present and sufficient collateral and liquidity are available, an incentives-driven system will fail if profit opportunities are not actually taken.

Mechanics explained:

- Interaction providers (IPs) can commit funds to an “interactions contract” (IC) in return for IP-tokens.
- This interaction contract takes profit opportunities across mento and DEXs in a way that is beneficial to the cStables stability and general price efficiency on chain.
- The IC receives privileged access to certain reserve interactions such that arbitrage profit opportunities are better democratized and MEV is reduced
- The interactions that this contract triggers are defined by a convex optimization problem.
- Convex min objective, convex inequality constraints, affine equ. constraints
- Guaranteed execution, off-chain optimization and on-chain proof: Everyone can provide the solution to this optimization problem to the contract that then checks the validity of this solution by checking the KKT conditions. Executing this contract will be rather cheap (checking a set of linear equations and inequalities), so everyone who has an incentive to keep Mento healthy, like CPs, has a strong incentive to trigger IC execution - it only needs one bot to trigger this for the entirety of the capital in the IC contract to be put to productive use.
- IP tokens received by interaction providers can be long-term locked / farmed similarly to the CP of collateral providers:
- For sources of rewards, see CPs
- As with CPs, funds to the IC have to be provided in the same proportions as current contract holdings of the other ICs in order to achieve IP-token fungibility. As with LP-tokens and CP-tokens, IP-tokens are redeemable for funds in the IP contract on a pro-rata basis.

Guaranteed interactions via “Interaction Farming” - what it achieves:

- “Guaranteed” healthy stability protocol interactions - also during crisis periods /  black-swan events
- Increased on-chain market efficiency
- Increased user participation and democratization of arbitrage profits
- Innovative new earning opportunities for defi users and which fosters engagement and growth. IP rewards can be expected to be sustainable income as they are a compensation for solving an actual problem - guaranteeing healthy protocol interactions, also during crisis periods.
