"""
Provides OracleProvider class for OracleRateGenerator
"""

from uuid import UUID
from model.types import OracleConfig
from model.utils.rng_provider import rngp
from model.constants import blocktime_seconds


class OracleProvider():
    """
    Oracle provider
    """
    name: str
    id_: UUID
    config: OracleConfig

    def __init__(self, name: str, oracle_id: UUID, config: OracleConfig):
        self.name = name
        self.orace_id = oracle_id
        self.config = config
        self.rng = rngp.get_rng("Oracle", oracle_id)
        self.reports = {pair: None for pair in config.pairs}

    def update(self, state_history, prev_state):
        """
        Updates reports
        """
        if prev_state['timestep'] == 1:
            oracle_report = {
                pair: prev_state['market_price'].get(pair) for pair in self.config.pairs
            }
            self.reports = oracle_report
        else:
            delay = min(self.config.delay, prev_state['timestep']-1)
            oracle_report = {
                pair: state_history[-delay][-1]['market_price'].get(pair)
                for pair in self.config.pairs}
            if self.identify_outdated_reports(oracle_report, prev_state):
                self.reports = oracle_report

    def identify_outdated_reports(self, oracle_report, prev_state):
        """
        returns list of pairs that are outdated
        """
        update_required = ((blocktime_seconds * prev_state['timestep']) %
                           self.config.reporting_interval == 0)

        if update_required:
            outdated_pairs = self.reports.keys()
        else:
            outdated_pairs = [pair for pair in self.config.pairs if
                            abs(prev_state['oracle_rate'].get(pair) -
                                    oracle_report[pair]) > 1 +
                                self.config.price_threshold]
        return outdated_pairs
