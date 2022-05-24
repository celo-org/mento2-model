"""
oracle generator and related functions
"""

from typing import Dict
from uuid import UUID, uuid4, uuid5
import numpy as np


from model.entities.oracle_provider import OracleProvider
from model.types import AggregationMethod, Oracles
from model.utils.generator import Generator
from model.utils.rng_provider import rngp

ACCOUNTS_NS = uuid4()

# raise numpy warnings as errors
np.seterr(all='raise')


class OracleRateGenerator(Generator):
    """
    This class is providing a market environment
    """
    oracles_by_id: Dict[UUID, OracleProvider] = {}

    def __init__(
        self,
        oracles: Oracles
    ):
        self.input = None
        self.rng = rngp.get_rng("OracleGenerator")
        for (oracle_type, oracle_params) in oracles.items():
            for index in range(oracle_params.count):
                self.create_oracle(
                    oracle_name=f"{oracle_type}_{index}",
                    aggregation=oracle_params.aggregation,
                )

    @classmethod
    def from_parameters(cls, params, _initial_state):
        oracle_generator = cls(params['oracles'])
        return oracle_generator

    def create_oracle(self, oracle_name: str, aggregation: AggregationMethod):
        oracle_provider = OracleProvider(oracle_name=oracle_name,
                                         oracle_id=uuid5(ACCOUNTS_NS, oracle_name),
                                         aggregation=aggregation, delay=10
                                         )
        self.oracles_by_id[oracle_provider.oracle_id] = oracle_provider
        return oracle_provider

    def delay(self):
        """
        Delay function for advanced delaying or different delay types (e.r. random)
        """

    def exchange_rate(self, state_history, prev_state):
        exchange_rate = self.aggregation(state_history, prev_state)
        return exchange_rate

    def aggregation(self, state_history, prev_state):
        oracle_reports = [oracle.report(state_history, prev_state)
                          for _oracle_id, oracle in self.oracles_by_id.items()]
        return oracle_reports[0]
