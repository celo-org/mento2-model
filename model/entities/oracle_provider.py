"""
Provides OracleProvider class for OracleRateGenerator
"""

import numpy as np
from model.types import AggregationMethod
from model.utils.rng_provider import rngp


class OracleProvider():
    """
    Oracle provider
    """

    def __init__(self, oracle_name, oracle_id, aggregation, delay):
        self.name = oracle_name
        self.oracle_id = oracle_id
        self.aggregation_method = aggregation
        self.delay = delay
        self.reports = {'celo_usd': None}
        self.rng = rngp.get_rng("Oracle")

    def aggregation(self, _state_history, prev_state):
        if isinstance(self.aggregation_method, AggregationMethod):
            oracle_report = prev_state["market_price"]['celo_usd']
        self.reports['celo_usd'] = np.concatenate((self.reports, oracle_report))

    def report(self, state_history, prev_state):
        oracle_report = {}
        for ticker, _report_log in self.reports.items():
            if prev_state['timestep'] == 1:
                oracle_report[ticker] = prev_state['market_price'][ticker]
            else:
                # seems state_history only contains last step if substeps are not saved
                oracle_report[ticker] = state_history[-self.delay][-1]['market_price'][ticker]
        return oracle_report
