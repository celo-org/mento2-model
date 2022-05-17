# Generators

Generator are classes that hold state and logic that the simulation depends on, but which would be cumbersome to implement purely as policy functions and would end up bloating the simulation state.
They also provide a nice way of structuring the simulation logic in modules.

## Relationship between radCad and Generators

### The custom Engine

Generators live for the duration of a simulation run and they are seeded with the simulation parameters for that run. This is achieved by creating a custom `Engine` that extends `radcad.Engine`, it is located in `model/utils/engine.py`.

> For the purpose of this document we will differentiate between the simulation `params`, which is the base params of the simulation defined in `model/system_parameters.py` and the `run_params` which is the result of radCad's parameter sweep which generates specific params for each simulation run.

This `Engine` extends the base engine in two ways:

1. It injects a `GeneratorContainer` into the `run_param` which is then responsible for instantiating Generators with the current run's `run_params`.
2. It processes the `state_update_blocks` passed into the simulation and injects dynamic state updated blocks from Generators.

### Using Generators

There two major ways of interacting with Generators that we will explore:

- Inject them into policy functions that rely on their internal state - i.e. the one that's not saved to the simulation state.
- Inject their dynamic `state_update_blocks` into the simulation.

#### Injecting them into policy functions

```python
@inject(AccountGenerator)
def p_epoch_rewards(params, substep, state_history, prev_state,
                           account_generator=AccountGenerator):
    # ...
```

> See `parts/celo_system.py`

This is an example of how to inject a Generator into a policy function and both consume and mutate the generator's state.

#### Injecting dynamic `state_update_blocks`

State update blocks:

```python
_state_update_blocks = [
    state_update_block_market_price_change,
    state_update_block_periodic_mento_bucket_update,
    generator_state_update_block(AccountGenerator, "traders"), # <- here
    state_update_block_epoch_rewards,
    # generator_state_update_block(AccountGenerator, "checkpoint")
    state_update_block_price_impact,
]
```

> see `model/state_update_blocks.py`

AccountGenerator:

```python
class AccountsGenerator(Generator):
    # ....
    @state_update_blocks("traders")
    def traders_execute(self):
        return [
            {
                "description": f"""
                    Trader update blocks for {trader.account_id}
                """,
                "policies": {
                    "trader_policy": self.get_trader_policy(trader.account_id)
                },
                "variables": {
                    "mento_buckets": update_from_signal("mento_buckets"),
                    "reserve_balance": update_from_signal("reserve_balance"),
                    "floating_supply": update_from_signal("floating_supply"),
                },

            } for trader in self.traders()
        ]

    def get_trader_policy(self,account_id):
        def policy(params, substep, state_history, prev_state):
            trader = self.get(account_id)
            return trader.execute(params, substep, state_history, prev_state)
        return policy
```

In order to link generator defined state update blocks to the simulation one has to define a function in the generator and decorate it with the `state_update_blocks` decorator which receives a tag (in this case `traders`) which is an arbitrary string. Then in the simulation `state_update_blocks` array use the `generator_state_update_block` helper, passing in the generator class and selector.
This allows us to implement multiple dynamic state update block types in a single generator and control the ordering.
