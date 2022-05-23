
"""
# Oracles related Update and Policy functions
"""
from model.generators.oracles import OracleRateGenerator
from model.parts.buy_and_sell import buckets_should_be_reset
from model.utils.generator_container import inject


@inject(OracleRateGenerator)
def p_oracle_report(
    params,
    _substep,
    state_history,
    prev_state,
    oracle_rate_generator: OracleRateGenerator,
):
    """
    Updates the median rate to update the Mento buckets
    """
    if (prev_state['timestep'] > 1) and buckets_should_be_reset(params, prev_state):
        oracle_rates = oracle_rate_generator.exchange_rate(state_history, prev_state)
    else:
        oracle_rates = prev_state['oracle_rate']
    return {'oracle_rate': oracle_rates}
