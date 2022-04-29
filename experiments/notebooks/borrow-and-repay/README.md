# Borrow and Repay

Mento stable assets can currently come into existence by buying them from Mento, through Granda Mento and as validator rewards. Giving users the ability to lock collateral in IRPs (individual reserve positions) and mint stable assets against it, would introduce a new mechanism with parameters to modulate the inflation of stable assets. It would allow for more exotic reserve assets to be used as collateral with granularly set minimum reserve ratios and caps, which serve to further diversify the makeup of reserves. IRPs can also make it possible to mint Mento stable assets locally on different chains but still have them tied into the base reserve the lives on the Celo blockchain.

In the context of debt-based stability protocols, liquidation serves as a mechanism to contract the stable asset supply in order to increase the overall collateralization of the protocol.

The core innovation of Mento IRPs compared to the Maker-type model is that instead of triggering auction-based fire sales of collateral whenever a position becomes undercollateralized, collateral is simply returned to the base reserve in case of a liquidation. This is possible through leveraging the buy&sell feature of Mento that can handle the contraction of stable assets if necessary such that fire sale auctions as in Maker-type models are not required.

Such a mechanism can be achieved using a keeper model, in which agents are incentivize to execute liquidations on IRPs, transferring the confiscated collateral to the base reserve, and no other change needs to happen to the protocol.

But a more interesting approach is to expose a method on IRPs that would allow the `exchange` to redeem a variable amount of the underlying collateral only as long as the IRP is undercollateralized. This could allow a mechanism where Mento pays out Celo not only from the reserve but also by dipping into IRPs using an off-chain routing mechanism. Which would still need to be incentivize but in a way similar to how Liquity uses kickback rate for frontends.

Trading with Mento Buy&Sell could happen in two ways:

- Direct trading with funds from the base reserve (what’s happening currently)
- Provide one or more IRPs that can be drained of collateral as part of the trade transaction and an address for getting a kickback from the spread of the swap.

This incentivizes applications that consume Mento (Valora, celoterminal, etc) to take on the role of keepers. It would also allow arbitrageurs to essentially become keepers without having to add complexity to their setup; they can get a discount when buying Celo from Mento if they route the order through liquidatable IRPs.

Depending on the collateral backing the IRP we would require Mento’s Exchange to support trading with any of the supported reserve collateral, or otherwise require a liquid market to convert to Celo.
