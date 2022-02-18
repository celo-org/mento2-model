"""
# Defines Actors. Actors:
 *have an account
 *have a strategy (see strategies.py) attached to it
 *get optimal action from strategy conditional on params, prev_state, ...
 *trigger optimal action via action manager
"""
from typing import List
from strategies import BuyAndSellArb
from model.state_update_blocks import account_manager, actor_manager, buy_and_sell_manager


def p_create_actors(params, substep, state_history, prev_state):
    if len(state_history) == 1:
        actor_manager.reset()
        if params['arb_actor_enabled']:
            actor_manager.create_new_funded_actor(
                celo=params['arb_actor_init_celo_balance'],
                cusd=params['arb_actor_init_cusd_balance'],
                strategy_type='buy_and_sell_arb'
            )


class Actor:
    def __init__(self, actor_id, account_id, strategy):
        self.actor_id = actor_id
        self.account_id = account_id
        self.strategy = strategy

    def state_update_block(self):
        description = self.strategy.decription
        policies = self.strategy.policies
        state_variables_after_action = self.strategy.state_variables_after_action
        state_update_block_actor = {
            f"description": f"""
                {description}
            """,
            'policies': policies,
            'variables': state_variables_after_action
        }
        return state_update_block_actor


class ActorManager:
    def __init__(self):
        self.all_actors: List[Actor] = []
        self.total_number_of_actors = 0

    def create_new_funded_actor(self, celo, cusd, strategy_type):
        account_id = account_manager.create_funded_account(
            celo=celo,
            cusd=cusd
        )
        actor_id = self.total_number_of_actors

        # TODO: Allow selection by strategy_type input
        if strategy_type == 'buy_and_sell_arb':
            strategy = BuyAndSellArb()
        else:
            raise 'Strategy type not recognized'

        new_funded_actor = Actor(
            actor_id=actor_id,
            account_id=account_id,
            strategy=strategy
        )
        self.all_actors.append(
            new_funded_actor
        )
        self.total_number_of_actors += 1
        return actor_id

    def get_all_actor_state_update_blocks(self):
        all_actor_state_update_blocks = []
        for actor in self.all_actors:
            all_actor_state_update_blocks.append(
                actor.state_update_block()
            )
        return all_actor_state_update_blocks

    def reset(self):
        self.__init__()
        print('actor_manager reset!')