"""
# Defines Actors. Actors:
 *have an account
 *have a strategy (see strategies.py) attached to it
 *get optimal action from strategy conditional on params, prev_state, ...
 *trigger optimal action via action manager
"""
from typing import List
from celo_system import account_manager
from strategies import BuyAndSellArb


class Actor:
    def __init__(self, actor_id, account_id, strategy):
        self.actor_id = actor_id
        self.account_id = account_id
        self.strategy = strategy


class ActorManager:
    def __init__(self):
        self.all_actors: List[Actor] = []
        self.total_number_of_actors = 0

    def create_new_funded_actor(self, celo, cusd, strategy_type='BuyAndSellArb'):
        account_id = account_manager.create_funded_account(
            celo=celo,
            cusd=cusd
        )
        actor_id = self.total_number_of_actors

        # TODO: Allow selection by strategy_type input
        strategy = BuyAndSellArb()

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

    def trigger_optimal_action(self, actor_id, params, prev_state):
        assert self.all_actors[actor_id].actor_id == actor_id, 'Actor_id mismatch!'
        state_variables_after_optimal_action = self.all_actors[actor_id].strategy.execute_optimal_action(
            params=params,
            prev_state=prev_state
        )
        return state_variables_after_optimal_action

    def reset(self):
        self.__init__()
        print('actor_manager reset!')