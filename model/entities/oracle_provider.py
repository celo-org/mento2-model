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
        self.reports = {ticker: None for ticker in config.tickers}

    def update(self, state_history, prev_state):
        """
        Updates reports
        """
        if prev_state['timestep'] == 1:
            oracle_report = {
                ticker: prev_state['market_price'][ticker] for ticker in self.reports}
            self.reports = oracle_report
        else:
            delay = min(self.config.delay, prev_state['timestep']-1)
            oracle_report = {
                ticker: state_history[-delay][-1]['market_price'][ticker]
                for ticker in self.reports}
            if self.identify_outdated_reports(oracle_report, prev_state):
                self.reports = oracle_report

    def identify_outdated_reports(self, oracle_report, prev_state):
        """
        returns list of tickers that are outdated
        """
        update_required = ((blocktime_seconds * prev_state['timestep']) %
                           self.config.reporting_interval == 0)

        if update_required:
            outdated_tickers = self.reports.keys()
        else:
            outdated_tickers = [ticker for ticker in self.reports if
                                abs(prev_state['oracle_rate'][ticker] -
                                    oracle_report[ticker]) > 1 +
                                self.config.price_threshold]
        return outdated_tickers
