"""
# Defines Actors. Actors:
 *have an account
 *have a strategy (see strategies.py) attached to it
 *get optimal action from strategy conditional on params, prev_state, ...
 *trigger optimal action via action manager
"""
from typing import List
from copy import deepcopy

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
class Actor:
    def __init__(self, actor_id, account_id, strategy):
        self.actor_id = actor_id
        self.account_id = account_id
        self.strategy = strategy


# pylint: disable=missing-class-docstring
class ActorManager:
    def __init__(self, account_manager, buy_and_sell_manager):
        self.all_actors: List[Actor] = []
        self.total_number_of_actors = 0
        self.account_manager = account_manager
        self.buy_and_sell_manager = buy_and_sell_manager

    # pylint: disable=missing-function-docstring
    def create_new_funded_actor(self, celo, cusd, strategy):
        account_id = self.account_manager.create_funded_account(celo=celo, cusd=cusd)
        actor_id = self.total_number_of_actors

        # TODO: Allow selection by strategy_type input
        new_funded_actor = Actor(
            actor_id=actor_id, account_id=account_id, strategy=strategy
        )
        self.all_actors.append(new_funded_actor)
        self.total_number_of_actors += 1
        return actor_id

    def all_actors_act(self):
        # TODO: Allow for more than one actor (make sure state variable updates happen correctly)
        state_variables_after_action = self.all_actors[
            0
        ].strategy.execute_optimal_action()
        return state_variables_after_action

    def reset(self, sell_max_strategy):
        self.__init__(self.account_manager, self.buy_and_sell_manager)
        # TODO: Make initial funding of actors a parameter
        # TODO: Allow for more than one actor
        self.create_new_funded_actor(
            celo=100000, cusd=100000, strategy=deepcopy(sell_max_strategy)
        )
        print("actor_manager reset!")
