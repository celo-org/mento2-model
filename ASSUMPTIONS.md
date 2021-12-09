# Model Assumptions

TBD

[comment]: <> (While the model implements the official Ethereum Specification wherever possible – see [README]&#40;README.md&#41; for latest implemented release version – and allows for the computational simulation of many different assumption scenarios, the model does rest on a few validator-level assumptions by default, described in this document and to a large degree sourced from the extensive research done in the context of the well-known [Hoban/Borgers Ethereum 2.0 Economic Model]&#40;https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE&#41;. We adapted some of these assumptions to reflect the evolution of the Ethereum protocol &#40;e.g., Altair updates&#41; and added new ones due to the nature of our dynamical-systems-modelling paradigm &#40;e.g. time-dependent, dynamic variables&#41;. The [Experiment Notebook: Model Validation]&#40;experiments\notebooks\1_model_validation.ipynb&#41; validates selected outputs of the CADLabs model against the Hoban/Borgers model to allow for efficient sanity checks. )
  
[comment]: <> (* [Network-level Assumptions]&#40;#network-level-assumptions&#41;)

[comment]: <> (  * [ETH Price]&#40;#ETH-Price&#41;)

[comment]: <> (  * [Proof-of-Work ETH Issuance]&#40;#proof-of-work-eth-issuance&#41;)

[comment]: <> (  * [Upgrade Stage Dates]&#40;#Upgrade-Stage-Dates&#41;)

[comment]: <> (    * [Simulation Start Date]&#40;#Simulation-Start-Date&#41;)

[comment]: <> (    * [EIP-1559 Activation Date]&#40;#eip-1559-activation-date&#41;)

[comment]: <> (    * [Proof-of-Stake Activation Date]&#40;#proof-of-stake-activation-date&#41;)

[comment]: <> (  * [Average Block Size]&#40;#Average-Block-Size&#41;)

[comment]: <> (  * [Average Base Fee]&#40;#Average-Base-Fee&#41;)

[comment]: <> (  * [Average Priority Fee]&#40;#Average-Priority-Fee&#41;)

[comment]: <> (  * [Maximum Extractable Value &#40;MEV&#41;]&#40;#maximum-extractable-value-mev&#41;)

[comment]: <> (* [Validator-level Assumptions]&#40;#validator-level-assumptions&#41;)

[comment]: <> (  * [Validator Adoption]&#40;#validator-adoption&#41;)

[comment]: <> (  * [Max Validator Cap]&#40;#maximum-validator-cap&#41;)

[comment]: <> (  * [Validator Environments]&#40;#validator-environments&#41;)

[comment]: <> (    * [Validator Environment Categories and Cost Structures]&#40;#Validator-Environment-Categories-and-Cost-Structures&#41;)

[comment]: <> (    * [Validator Environment Relative Weights]&#40;#Validator-Environment-Relative-Weights&#41;)

[comment]: <> (    * [Validator Environment Equal-slashing]&#40;#validator-environment-equal-slashing&#41;)

[comment]: <> (    * [Validator Environment Equal-uptime]&#40;#validator-environment-equal-uptime&#41;)

[comment]: <> (  * [Validator Performance]&#40;#Validator-Performance&#41;)

[comment]: <> (    * [Average Uptime]&#40;#Average-Uptime&#41;)

[comment]: <> (    * [Frequency of Slashing Events]&#40;#Frequency-of-Slashing-Events&#41;)

[comment]: <> (    * [Participation Rate]&#40;#Participation-Rate&#41;)

## Network-level Assumptions

### CELO Price 

TBD

To change this value, update the `celo_price_process` [System Parameter](./model/system_parameters.py).

[comment]: <> (### Proof-of-Work ETH Issuance)

[comment]: <> (The Proof-of-Work ETH issuance &#40;block rewards&#41; in all time-domain analyses before the model's PoS Activation Date is set to the mean daily issuance over the last 12 months from Etherscan. This value is constant and calculated from a CSV file in the [data/]&#40;data/&#41; directory, in the [data.historical_values]&#40;data/historical_values.py&#41; module.  )

[comment]: <> (To change this value, update the `daily_pow_issuance` [System Parameter]&#40;./model/system_parameters.py&#41;.)

[comment]: <> (Note: In future releases of this model, we may periodically update this value automatically until the merge. )

[comment]: <> (### Upgrade Stage Dates)

[comment]: <> (The model is configurable to reflect protocol behaviour at different points in time along the Ethereum development roadmap &#40;referred to as "upgrade stages" in this repo&#41;.)

[comment]: <> (#### Simulation Start Date)

[comment]: <> (In all state-space &#40;i.e. time-domain&#41; analyses of this repo, the default start date is set to the current date, i.e. all analyses start "today". That being said, there are certain Initial States and System Parameter default values that are static, and don't update dynamically from an API. In these cases we generally use an average value over a time period, for example for the validator adoption System Parameter.)

[comment]: <> (The simulation start date can be set using the `date_start` [System Parameter]&#40;./model/system_parameters.py&#41;. )

[comment]: <> (#### EIP-1559 Activation Date)

[comment]: <> (The model by default assumes 4 August 2021 [London mainnet upgrade]&#40;https://blog.ethereum.org/2021/07/15/london-mainnet-announcement/&#41; as the launch date for EIP1559. State-space &#40;i.e. time-domain&#41; analyses with starting date after 4 August 2021 therefore have the EIP-1559 mechanism fully activated. )

[comment]: <> (To change the EIP-1559 Activation Date, update the `date_eip1559` [System Parameter]&#40;./model/system_parameters.py&#41;.)

[comment]: <> (#### Proof-of-Stake Activation Date)

[comment]: <> (The model by default assumes 1 March 2022 for the Proof-of-Stake activation date &#40;"The Merge"&#41;, since this seemed to be the Ethereum Community's consensus expectation at the time the model's default assumptions were defined. Launch dates are hard to predict, hence we recommend to play with alternative dates.)

[comment]: <> (To change the Proof-of-Stake activation date, update the `date_pos` [System Parameter]&#40;./model/system_parameters.py&#41;.)

[comment]: <> (## Average Block Size)

[comment]: <> (With the introduction of [EIP-1559]&#40;https://eips.ethereum.org/EIPS/eip-1559&#41; the pre-EIP1559 block size &#40;gas limit&#41; has been replaced by two values: a “long-term average target” &#40;equal to the pre-EIP1559 gas limit, i.e. 15m gas&#41;, and a “hard per-block cap” &#40;set to twice the pre-EIP1559 gas limit, i.e. 30m gas&#41;. )

[comment]: <> (By default, the model assumes that the block size &#40;gas used per block&#41; will on average be equal to the gas target, i.e. 15m gas. To change this value, update the `gas_target_process` [System Parameter]&#40;./model/system_parameters.py&#41;.)

[comment]: <> (Note for cadCAD engineers: It is quite straight forward to extend the model for dynamic block size and base fee &#40;see [roadmap document]&#40;ROADMAP.md&#41;&#41;, and we encourage you to give this a try. This would also open the model up automatic updates via live adoption data.)

[comment]: <> (## Average Base Fee)

[comment]: <> ([EIP-1559]&#40;https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md&#41; defines a variable `max_fee_per_gas` to set a fee cap per transaction. This fee cap is the maximum fee in Gwei per gas a user will pay per transaction. This fee is made up of the base fee and a priority fee, where the base fee is burned and the priority fee is paid to miners/validators.)

[comment]: <> (The pre-EIP1559 blockspace market followed a demand curve - transactions with a higher value &#40;gas used x gas price&#41; are prioritized by miners over transactions with a lower value, and the total gas used in a block is limited to 15m.)

[comment]: <> (Effectively this meant that some transactions would be priced out and not included in the block. In practise, 10-15% of the gas used in a block is by zero-fee transactions, due to for example MEV clients including Flashbots bundles.)

[comment]: <> (For the above reason &#40;and until actual base fee data becomes available&#41;, instead of taking a historical minimum gas price per block to extrapolate to a reasonable future base fee at equilibrium, we take a 3 month median &#40;4 May 2021 - 4 August 2021&#41; to remove zero-fee outliers &#40;e.g. Flashbot bundles&#41; for pre-EIP-1559 date ranges &#40;zero fee transactions are no longer possible with EIP-1559&#41;.)

[comment]: <> (Using a [Dune Analytics query]&#40;https://duneanalytics.com/queries/91241&#41; we calculate the 90-day median gas price by transaction:)

[comment]: <> (* 90-Day 50th Percentile &#40;"Median"&#41;: 30 Gwei per gas)

[comment]: <> (To change the default average base fee, update the `base_fee_process` [System Parameter]&#40;./model/system_parameters.py&#41;.)

[comment]: <> (Note: In future releases of this model, we may periodically update this value automatically using on-chain data.)

[comment]: <> (### Average Priority Fee)

[comment]: <> (We used a staged approach for the estimation of the average priority fee:)

[comment]: <> (* Pre Proof-of-Stake: Priority Fee = 2 Gwei per gas &#40;to compensate for uncle risk and account for effect of possible sporadic transaction inclusion auctions&#41;)

[comment]: <> (* Post Proof-of-Stake: Priority Fee = 1 Gwei per gas &#40;no uncle risk to compensate for, i.e. only accounting for effect of possible sporadic transaction inclusion auctions&#41;)

[comment]: <> (Sources:)

[comment]: <> (* [Uncle risk/MEV miner fee calculation]&#40;https://notes.ethereum.org/@barnabe/rk5ue1WF_&#41;)

[comment]: <> (* [Why would miners include transactions at all]&#40;https://notes.ethereum.org/@vbuterin/BkSQmQTS8#Why-would-miners-include-transactions-at-all&#41;)

[comment]: <> (To change the default average priority fee, update the `priority_fee_process` [System Parameter]&#40;./model/system_parameters.py&#41;.)

[comment]: <> (### Maximum Extractable Value &#40;MEV&#41;)

[comment]: <> (The consensus among researchers is that MEV is hard to quantify, and the future interaction between EIP-1559 and MEV is at this stage uncertain and complex. For this reason we adopt the assumption that in normal conditions MEV will be extracted via off-chain mechanisms, and so will be treated as a seperate process to EIP-1559 - we suggest to refine the model assumptions once more data and research about the interaction between EIP-1559 and MEV is available.)

[comment]: <> (The `mev_per_block` [System Parameter]&#40;./model/system_parameters.py&#41; can be used to set the realized MEV in ETH per block. By default, we set the `mev_per_block` to zero ETH to better analyse PoS incentives in isolation, and leave it up to the reader to set their own assumptions. In some analyses we set the `mev_per_block` to the 3 month median value calculated using [Flashbots MEV-Explore analytics]&#40;https://explore.flashbots.net/&#41;.)

[comment]: <> (Note: In future releases of this model, we may periodically update this value automatically using API data.)

[comment]: <> (**Further reading:**)

[comment]: <> (Maximum Extractable Value &#40;MEV&#41;, previously referred to as "Miner Extractable Value", is a measure of the profit a miner/validator can make by arbitrarily including, excluding, or re-ordering transactions within the blocks they produce.)

[comment]: <> (The most prominent form of MEV has been that introduced by Flashbots' MEV-geth client, making up 85% of Ethereum's hashrate at the time of writing, and we include an extract from the research article by Flashbots ["MEV and EIP-1559"]&#40;https://hackmd.io/@flashbots/MEV-1559&#41; for context:)

[comment]: <> (> Flashbots has introduced a way for searchers to express their transaction ordering preferences to miners, leading to a more efficient market all Ethereum users should ideally benefit from. In order to achieve this, Flashbots provides custom mining software &#40;MEV-geth&#41; to a number of miners jointly controlling the vast majority of Ethereum’s hashrate &#40;85% at the time of writing&#41;.)

[comment]: <> (There are several auction mechanisms coexisting in Ethereum, identified by Flashbots in their research article ["MEV and EIP-1559"]&#40;https://hackmd.io/@flashbots/MEV-1559&#41;. Of these MEV related auction mechanisms only one, transaction inclusion, directly affects EIP-1559 priority fees:)

[comment]: <> (* Transaction inclusion via EIP-1559 priority fees)

[comment]: <> (* Transaction privacy via Flashbots/Darkpools)

[comment]: <> (* Transaction ordering via Flashbots/Other relays)

[comment]: <> (Prior to the adoption of the Flashbots MEV-geth client, gas prices were artificially high due to MEV bots spamming blocks with higher gas bids to ensure their transaction would occur before the transaction that they were attacking. Since then, the majority of MEV bots have moved to the Flashbots network, relieving the network of this spam that drove gas prices up. Now that MEV is extracted on an independent channel &#40;Flashbots&#41; and from a different mechanism &#40;shared profit vs. high gas fees&#41;, gas prices have decreased.)

[comment]: <> (## Validator-level Assumptions)

[comment]: <> (### Validator Adoption)

[comment]: <> (Validator adoption is the assumed rate of new validators entering the activation queue per epoch, that results in an implied ETH staked value over time.)

[comment]: <> (The "Validator Revenue and Profit Yields" experiment notebook introduces three linear adoption scenarios &#40;historical adoption has been approximately linear&#41;:)

[comment]: <> (* Normal adoption: assumes an average of 3 new validators per epoch. These rates correspond to the historical average newly **activated** validators per epoch between 15 January 2021 and 15 July 2021 as per [Beaconscan]&#40;https://beaconscan.com/stat/validator&#41;.)

[comment]: <> (* Low adoption: assumes an average of 1.5 new validators per epoch, i.e. a 50% lower rate compared to the base scenario)

[comment]: <> (* High adoption: assumes an average of 4.5 new validators per epoch, i.e. a 50% higher rate compared to the base scenario)

[comment]: <> (The activation queue is modelled as follows: Validators that deposit 32 ETH are only activated and allowed to validate once they pass through the queue, and the queue has a maximum rate at which it can process and activate new validators. This activation rate is what changes the effective validator adoption rate in some analyses where there are more validators wanting to enter the system than being activated per epoch.)

[comment]: <> (The normal adoption scenario is used as the default validator adoption rate for all experiments - to change this value, update the `validator_process` [System Parameter]&#40;./model/system_parameters.py&#41;.)

[comment]: <> (### Maximum Validator Cap)

[comment]: <> (The model adds a feature of a maximum validator cap to limit the number of validators that are validating &#40;"awake"&#41; at any given time.)

[comment]: <> (This feature is based on Vitalik's proposal where validators are not stopped from depositing and becoming active validators, but rather introduces a rotating validator set.)

[comment]: <> ("Awake" validators are a subset of "active" validators that are "validating" and receiving rewards, while "active" validators are all the validators with ETH staked.)

[comment]: <> (The maximum validator cap is disabled by default &#40;by setting the value to `None`&#41;, it's value is defined by the `MAX_VALIDATOR_COUNT` system parameter.)

[comment]: <> (See https://ethresear.ch/t/simplified-active-validator-cap-and-rotation-proposal for additional context.)

[comment]: <> (### Validator Environments)

[comment]: <> (The model supports the simulation of validator economics across different "validator environments" to account for the different deployment setups validators are using to access the network, each with slightly different economics. )

[comment]: <> (#### Validator Environment Categories and Cost Structures)

[comment]: <> (By default, the model implements the 7 validator environment categories as suggested by )

[comment]: <> ([Hoban/Borgers Ethereum 2.0 Economic Model]&#40;https://thomasborgers.medium.com/ethereum-2-0-economic-review-1fc4a9b8c2d9&#41;. Below is a short characterization of each category. For the respective hardware-setup and cost-assumption details, please refer to ["Cost of Validating"]&#40;https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE&#41;.)

[comment]: <> (1. **Run own hardware validator &#40;"DIY-Hardware"&#41;**)

[comment]: <> (- Setup: Individual running a Beacon Node and Validator Client with one or more Validators on their own hardware)

[comment]: <> (- Economics: Individual receives full revenue yields and carries full hardware, electricity, and bandwidth cost)

[comment]: <> (2. **Run own cloud validator &#40;"DIY-Cloud"&#41;**)

[comment]: <> (- Setup: Individual running a Beacon Node and Validator Client with one or more Validators on a cloud service)

[comment]: <> (- Economics: Individual receives full revenue yields and carries cost of cloud service, with costs shared amongst multiple Validators for a lower cost per Validator compared to DIY hardware)

[comment]: <> (3. **Validate via a pool Staking-as-a-Service provider &#40;"Pool-StaaS"&#41;**)

[comment]: <> (- Setup: Individual staking indirectly in a pool of Validators via a Staking-as-a-Service provider with infrastructure &#40;Beacon Node and Validator Client&#41; and keys managed by provider)

[comment]: <> (- Economics: Costs &#40;hardware, electricity, and bandwidth&#41; carried by StaaS provider who charges a fee &#40;percentage of revenue&#41; to the Validators in pool)

[comment]: <> (4. **Validate via a pool hardware service provider &#40;"Pool-Hardware"&#41;**)

[comment]: <> (- Setup: A node operator hosts both a Beacon Node and Validator Client on their own hardware infrastructure, and pools ETH together from Stakers to create multiple Validators)

[comment]: <> (- Economics: Costs &#40;hardware, electricity, and bandwidth&#41; and revenue yields shared amongst Validators in pool)

[comment]: <> (5. **Validate via a pool cloud provider &#40;"Pool-Cloud"&#41;**)

[comment]: <> (- Setup: A node operator hosts both a Beacon Node and Validator Client on their own cloud infrastructure, and pools ETH together from Stakers to create multiple Validators)

[comment]: <> (- Economics: Costs &#40;hardware, electricity, and bandwidth&#41; and revenue yields shared amongst Validators in pool)

[comment]: <> (6. **Validate via a custodial Staking-as-a-Service provider &#40;"StaaS-Full"&#41;**)

[comment]: <> (- Setup: Validator stakes via a custodial Staking-as-a-Service provider, that manages both the Validator Client and Beacon Node)

[comment]: <> (- Economics: Operational costs &#40;hardware, electricity, and bandwidth&#41; carried by StaaS provider who charges a fee &#40;percentage of revenue&#41; to the Validators)

[comment]: <> (7. **Validate via a non-custodial Staking-as-a-Service provider &#40;"StaaS-Self-custodied"&#41;**)

[comment]: <> (- Setup: Validator stakes using own Validator Client, but instead of running a Beacon Node themselves they opt to use a StaaS Beacon Node provider via an API)

[comment]: <> (- Economics: Beacon Node operational costs &#40;hardware, electricity, and bandwidth&#41; carried by StaaS provider who charges a fee &#40;percentage of revenue&#41; to the Validators &#40;assumes lower cost than Staas-Full environment&#41;)

[comment]: <> (This model allows for the creation of **custom validator environments and cost-structures**. These can be configured in the model's [System Parameters]&#40;model/system_parameters.py&#41; as part of the `validator_environments` variable.)

[comment]: <> (For more information about currently active validator staking services, see https://beaconcha.in/stakingServices.)

[comment]: <> (#### Validator Environment Relative Weights)

[comment]: <> (By default, the model assumes the following relative weights for the calculation of average validator revenue and profit yields, as defined by )

[comment]: <> ([Hoban/Borgers' Ethereum 2.0 Economic Model]&#40;https://docs.google.com/spreadsheets/d/1y18MoYSBLlHZ-ueN9m0a-JpC6tYjqDtpISJ6_WdicdE&#41;. These values could change substantially and the user is encouraged to experiment with other assumptions. )

[comment]: <> (1. Run own hardware validator &#40;"DIY-Hardware"&#41;: **37%**)

[comment]: <> (2. Run own cloud validator &#40;"DIY-Cloud"&#41;: **13%**)

[comment]: <> (3. Validate via a pool Staking-as-a-Service provider &#40;"Pool-Staas"&#41;: **27%**)

[comment]: <> (4. Validate via a pool hardware service provider &#40;"Pool-Hardware"&#41;: **5%**)

[comment]: <> (5. Validate via a pool Cloud provider &#40;"Pool-Cloud"&#41;: **2%**)

[comment]: <> (6. Validate via a custodial Staking-as-a-Service provider &#40;"StaaS-Full"&#41;: **8%**)

[comment]: <> (7. Validate via a non-custodial Staking-as-a-Service provider &#40;"StaaS-Self-custodied"&#41;: **8%**)

[comment]: <> (#### Validator Environment Equal-slashing)

[comment]: <> (Whereas in reality slashing events have occurred more often in some validator environments &#40;e.g. institutional players getting their setup wrong and double-signing&#41;, we make the simplifying assumption that slashing events are applied equally across all validator-environment types.)

[comment]: <> (This assumption is adequate for calculations of validator economics under steady-state conditions but might fail if slashing events increase significantly for a specific validator-environment type, or if the network is under attack by a specific validator-environment type.)

[comment]: <> (See https://youtu.be/iaAEGs1DMgQ?t=574 for additional context. )

[comment]: <> (#### Validator Environment Equal-uptime)

[comment]: <> (Whereas we arguably expect better uptime for some validator environments than others &#40;e.g. better for cloud environments than local hardware environments&#41;, we make the simplifying assumption that the same validator uptime is applied to all validator environments. Once respective data becomes available over time, this assumption could be dropped in future model iterations.)

[comment]: <> (### Validator Performance)

[comment]: <> (#### Average Uptime)

[comment]: <> (By default, the model assumes an average of 98% uptime.)

[comment]: <> (In reality, this value has varied between lows of 95% and highs of 99.7% with an average of approximately 98%.)

[comment]: <> (We capture the average uptime using the `validator_uptime_process` System Parameter – a function that returns the average uptime and allows us to create stochastic or time-dependent uptime processes.)

[comment]: <> (#### Frequency of Slashing Events)

[comment]: <> (By default, the model assumes 1 slashing event every 1000 epochs.)

[comment]: <> (As more statistical data is collected about slashing in different validator environments, this assumption could be updated.)

[comment]: <> (#### Participation Rate)

[comment]: <> (The model assumes that validators are either online and operating perfectly, or offline and not fulfilling their duties. Offline validators are penalized for not attesting to the source, target, and head. We do not model validators that fulfil some of their duties, and not other duties. We capture this participation rate &#40;percentage of online validators&#41; using the `validator_uptime_process` System Parameter.)

[comment]: <> (In its initial version, the model does not model Ethereum's inactivity leak mechanism. We assume a **participation of more than 2/3 at all times**. We assert this requirement in the `policy_validators&#40;...&#41;` Policy Function.)
