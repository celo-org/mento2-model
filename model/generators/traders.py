"""
Provides Traders / Actors
"""

import cvxpy
from cvxpy import Maximize, Minimize, Problem, Variable
import numpy as np

from experiments import simulation_configuration

from model.parts import buy_and_sell
from model.parts.strategies import StrategyAbstract


class AccountHolder:
    """
    Agent / Account Holder
    """

    def __init__(
        self, parent, account_id, account_name, balance, account_type=None, orders=None
    ):
        self.parent = parent
        self.account_id = account_id
        self.account_name = account_name
        self.balance = {"celo": balance["celo"], "cusd": balance["celo"]}
        self.account_type = account_type
        self.strategy = RandomTrading(self)
        self.orders = orders
        self.generate_sell_amounts()

    def generate_sell_amounts(
        self,
        blocks_per_timestep=simulation_configuration.BLOCKS_PER_TIMESTEP,
        timesteps=simulation_configuration.TIMESTEPS,
    ):
        """
        This function generates lognormal returns
        """
        # timesteps_per_year = constants.blocks_per_year // blocks_per_timestep
        sample_size = timesteps * blocks_per_timestep + 1
        # TODO parametrise random params incl. seed
        sell_gold = np.random.binomial(1, 0.5, sample_size)
        orders = np.vstack(
            [sell_gold, np.abs(np.random.normal(100, 5, size=sample_size))]
        )
        self.orders = np.core.records.fromarrays(
            orders, names=["sell_gold", "sell_amount"]
        )

    def current_orders(self, state):
        return self.orders[:, state]

    def execute(
        self,
        params,
        substep,
        state_history,
        prev_state,
    ):
        """
        Making pylint happy
        """
        order = self.strategy.return_optimal_trade(params, prev_state)
        sell_amount = order["sell_amount"]
        sell_gold = order["sell_gold"]
        states, deltas = buy_and_sell.exchange(
            params, sell_amount, sell_gold, substep, state_history, prev_state
        )
        # TODO this has to happen hear to avoid circular referencing, find better solution
        self.parent.change_account_balance(
            self.account_id, deltas["cusd"], deltas["celo"], self.account_type
        )
        self.parent.change_reserve_account_balance(delta_celo=deltas["celo"])
        return states


# pylint: disable=using-constant-test
class RandomTrading(StrategyAbstract):
    """
    Random Trading
    """

    def __init__(self, parent, acting_frequency=1):
        # The following is used to define the strategy and needs to be provided in subclass
        super().__init__(parent, acting_frequency)
        self.generate_sell_amounts()

    def sell_gold(self, prev_state):
        # Arb trade will sell CELO if  CELO/USD > CELO/cUSD
        return self.orders[prev_state["timestep"]]["sell_gold"]

    def define_variables(self):
        self.variables["sell_amount"] = Variable(pos=True)

    def define_expressions(self, params, prev_state):
        """
        Defines and returns the expressions (made of variables and parameters)
        that are used in the optimization
        """

    def define_objective_function(self, params, prev_state):
        """
        Defines and returns the cvxpy objective_function
        """
        self.objective_function = self.variables["sell_amount"]
        self.optimization_direction = "maximize"

    def define_constraints(self, params, prev_state):
        """
        Defines and returns the constraints under which the optimization is conducted
        """
        self.constraints = []
        # TODO: Get budget based on account
        max_budget_cusd = self.parent.balance["cusd"]
        max_budget_celo = self.parent.balance["celo"]
        if self.sell_gold(prev_state):
            self.constraints.append(
                self.variables["sell_amount"]
                <= min(
                    max_budget_celo, self.orders[prev_state["timestep"]]["sell_amount"]
                )
            )
        else:
            self.constraints.append(
                self.variables["sell_amount"]
                <= min(
                    max_budget_cusd, self.orders[prev_state["timestep"]]["sell_amount"]
                )
            )

    def generate_sell_amounts(
        self,
        blocks_per_timestep=simulation_configuration.BLOCKS_PER_TIMESTEP,
        timesteps=simulation_configuration.TIMESTEPS,
    ):
        """
        This function generates lognormal returns
        """
        # timesteps_per_year = constants.blocks_per_year // blocks_per_timestep
        sample_size = timesteps * blocks_per_timestep + 1
        # TODO parametrise random params incl. seed
        sell_gold = np.random.binomial(1, 0.5, sample_size)
        orders = np.vstack(
            [sell_gold, np.abs(np.random.normal(100, 5, size=sample_size))]
        )
        self.orders = np.core.records.fromarrays(
            orders, names=["sell_gold", "sell_amount"]
        )

    def calculate(self, params, prev_state):
        """
        Calculates optimal trade if analytical solution is available
        """
        sell_amount = self.orders[prev_state["timestep"]]["sell_amount"]
        buy_amount = buy_and_sell.get_buy_amount(
            params=params,
            prev_state=prev_state,
            sell_amount=sell_amount,
            sell_gold=self.sell_gold(prev_state),
        )
        trade = {
            "sell_gold": self.sell_gold(prev_state),
            "sell_amount": sell_amount,
            "buy_amount": buy_amount,
        }
        return trade

    # pylint: disable=broad-except
    def solve(self, params, prev_state):

        # Generate cvxpy optimization problem
        assert (
            self.optimization_direction in ( "minimize", "maximize")
        ), "Optimization direction not specified."
        if self.optimization_direction == "minimize":
            obj = Minimize(self.objective_function)
        else:
            obj = Maximize(self.objective_function)
        prob = Problem(obj, self.constraints)

        # The optimization problem of SellMax is quasi-convex
        try:
            prob.solve(
                solver=cvxpy.ECOS,
                abstol=1e-6,
                reltol=1e-6,
                max_iters=10000,
                verbose=False,
            )

        except Exception as error:
            print(error)

        assert prob.status == "optimal", "Optimization NOT successful!"
        # print(f'Objective value in optimum is {prob.value}.')
        # print(self.variables['sell_amount'].value)
        # print(self.expressions['mento_rate_after_trade'].value)
        buy_amount = buy_and_sell.get_buy_amount(
            params=params,
            prev_state=prev_state,
            sell_amount=self.variables["sell_amount"].value,
            sell_gold=self.sell_gold(prev_state),
        )

        trade = {
            "sell_gold": self.sell_gold(prev_state),
            "sell_amount": self.variables["sell_amount"].value,
            "buy_amount": buy_amount,
        }
        return trade

    def optimize(self, params, prev_state):
        """
        Runs the optimization
        """
        self.define_variables()
        if self.calculate:
            optimal_trade = self.calculate(params, prev_state)
        else:
            self.define_expressions(params, prev_state)
            self.define_objective_function(params, prev_state)
            self.define_constraints(params, prev_state)
            optimal_trade = self.solve(params, prev_state)
        return optimal_trade

    def return_optimal_trade(self, params, prev_state):
        """
        Executes the optimal action depending on the optimization outcome
        """
        # if prev_state['timestep'] % self.acting_frequency != 0:
        #             # Actor not acting this timestep
        #             return self.buy_and_sell_manager.leave_all_state_variables_unchanged(
        #                 prev_state=prev_state,
        #                 policy_type='exchange'
        #             )

        trade = self.optimize(params, prev_state)

        # state_variables_state_after_trade = (
        #    self.buy_and_sell_manager.state_variables_state_after_trade(
        #        prev_state=prev_state, trade=optimal_trade
        #    )
        # )

        return trade
