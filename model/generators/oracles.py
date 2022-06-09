"""
oracle generator and related functions
"""

from typing import Dict, List
from uuid import UUID, uuid4, uuid5
import numpy as np


from model.entities.oracle_provider import OracleProvider
from model.types import Pair
from model.config_types import OracleConfig
from model.utils import update_from_signal
from model.utils.generator import Generator, state_update_blocks
from model.utils.rng_provider import rngp

ORACLES_NS = uuid4()

# raise numpy warnings as errors
np.seterr(all='raise')


class OracleRateGenerator(Generator):
    """
    This class is providing oracle rates and is responsible generating oracle providers
     and emulate the functionality of sorted_oracles.sol
    """
    oracles_by_id: Dict[UUID, OracleProvider]
    oracles_by_pair: Dict[Pair, List[OracleProvider]]
    oracle_pairs: List[Pair]

    def __init__(
        self,
        oracles: List[OracleConfig],
        oracle_pairs: List[Pair]
    ):
        self.input = None
        self.rng = rngp.get_rng("OracleGenerator")
        self.oracle_pairs = oracle_pairs
        self.oracles_by_pair = {pair: [] for pair in oracle_pairs}
        self.oracles_by_id = {}
        for oracle_config in oracles:
            for index in range(oracle_config.count):
                self.create_oracle(index, oracle_config)

    @classmethod
    def from_parameters(cls, params, _initial_state, _container):
        oracle_generator = cls(params['oracles'], params['oracle_pairs'])
        return oracle_generator

    def create_oracle(self, index: int, oracle_config: OracleConfig):
        """
        Creates Oracle Providers
        """
        oracle_name = f"{oracle_config.type}_{index}"
        oracle_id = uuid5(ORACLES_NS, oracle_name)

        oracle_provider = OracleProvider(name=oracle_name,
                                         oracle_id=oracle_id,
                                         config=oracle_config)
        self.oracles_by_id[oracle_id] = oracle_provider
        for pair in oracle_config.pairs:
            self.oracles_by_pair[pair].append(oracle_provider)

    def exchange_rate(self, state_history, prev_state):
        exchange_rate = self.aggregation(state_history, prev_state)
        return exchange_rate

    def aggregation(self, state_history, prev_state):
        self.update_oracles(state_history, prev_state)
        median_per_asset = {
            pair: np.median([
                oracle_provider.reports[pair]
                for oracle_provider in self.oracles_by_pair[pair]
            ] or [0])
            for pair in self.oracle_pairs
        }
        return median_per_asset

    def update_oracles(self, state_history, prev_state):
        for _id, oracle in self.oracles_by_id.items():
            oracle.update(state_history, prev_state)

    @state_update_blocks("report")
    def oracle_report(self):
        return [{
            "description": """
                updates the oracle rate
            """,
            "policies": {"oracle_rate": self.get_oracle_report_policy()},
            "variables": {
                "oracle_rate": update_from_signal("oracle_rate")},
        }]

    def get_oracle_report_policy(self):
        """
        Updates the median rate to update the Mento buckets
        """
        def p_oracle_report(
            _params,
            _substep,
            state_history,
            prev_state,
        ):
            oracle_rates = self.exchange_rate(state_history, prev_state)
            return {'oracle_rate': oracle_rates}
        return p_oracle_report
