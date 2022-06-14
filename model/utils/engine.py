"""
radCAD Engine extension to give us more control over how simulations happen
"""
import copy
from functools import reduce
from typing import Any, Callable, Dict, List, NamedTuple
from radcad.engine import Engine as RadCadEngine
from radcad import core, wrappers

from model.utils.rng_provider import RNGProvider

from .generator_container import GENERATOR_CONTAINER_PARAM_KEY, GeneratorContainer


class SimulationConfig(NamedTuple):
    params: Dict[str, Any]
    state: Dict[str, Any]
    state_update_blocks: List[Any]
    run_index: int

# pylint: disable=too-many-locals,protected-access,too-few-public-methods
class Engine(RadCadEngine):
    """
    Extends the radcad.Engine with the ability to:
    - Inject generators into a simulation run
    - Dynamically generate state update blocks based on the generators
    """

    def _run_stream(self, configs):
        simulations = [Engine._get_simulation_from_config(config) for config in configs]

        for simulation_index, simulation in enumerate(simulations):
            simulation.index = simulation_index

            timesteps = simulation.timesteps
            runs = simulation.runs
            initial_state = simulation.model.initial_state
            state_update_blocks = simulation.model.state_update_blocks
            params = simulation.model.params
            param_sweep = core.generate_parameter_sweep(params)

            self.executable._before_simulation(
                simulation=simulation
            )

            # NOTE Hook allows mutation of RunArgs
            for run_index in range(0, runs):
                if param_sweep:
                    context = wrappers.Context(
                        simulation_index,
                        run_index,
                        None,
                        timesteps,
                        initial_state,
                        params
                    )
                    self.executable._before_run(context=context)
                    for subset_index, param_set in enumerate(param_sweep):
                        context = wrappers.Context(
                            simulation_index,
                            run_index,
                            subset_index,
                            timesteps,
                            initial_state,
                            params
                        )
                        self.executable._before_subset(context=context)
                        config = __prepare_simulation_config__(SimulationConfig(
                                param_set,
                                initial_state,
                                state_update_blocks,
                                run_index))
                        yield wrappers.RunArgs(
                            simulation_index,
                            timesteps,
                            run_index,
                            subset_index,
                            copy.deepcopy(config.state),
                            config.state_update_blocks,
                            config.params,
                            self.deepcopy,
                            self.drop_substeps)
                        self.executable._after_subset(context=context)
                    self.executable._after_run(context=context)
                else:
                    context = wrappers.Context(
                        simulation_index,
                        run_index,
                        0,
                        timesteps,
                        initial_state,
                        params)
                    self.executable._before_run(context=context)
                    self.executable._before_subset(context=context)

                    config = __prepare_simulation_config__(SimulationConfig(
                            param_set,
                            initial_state,
                            state_update_blocks,
                            run_index))

                    yield wrappers.RunArgs(
                        simulation_index,
                        timesteps,
                        run_index,
                        0,
                        copy.deepcopy(config.state),
                        config.state_update_blocks,
                        config.params,
                        self.deepcopy,
                        self.drop_substeps,
                    )
                    self.executable._after_subset(context=context)
                    self.executable._after_run(context=context)

            self.executable._after_simulation(
                simulation=simulation
            )

def __inject_rng_provider__(config: SimulationConfig):
    config.params.update({
        'rngp': RNGProvider(config.params['rng_seed'], config.run_index)
    })
    return config

def __inject_generator_container__(config: SimulationConfig):
    config.params.update({
        GENERATOR_CONTAINER_PARAM_KEY: GeneratorContainer(
            copy.deepcopy(config.params),
            copy.deepcopy(config.state)
        )
    })
    return config

def __hydrate_state_update_blocks__(config: SimulationConfig):
    container = config.params.get(GENERATOR_CONTAINER_PARAM_KEY)
    flat_state_update_blocks = []
    for state_update_block in config.state_update_blocks:
        if state_update_block.get('type') == 'generator':
            generator = container.get(state_update_block.get('source'))
            selectors = state_update_block.get('selectors', [])
            flat_state_update_blocks += generator.state_update_blocks(selectors)
        else:
            flat_state_update_blocks += [state_update_block]

    return SimulationConfig(
        config.params,
        config.state,
        flat_state_update_blocks,
        config.run_index
    )

SimulationConfigModifier = Callable[[SimulationConfig], SimulationConfig]

MODIFIERS: List[SimulationConfigModifier] = [
    __inject_rng_provider__,
    __inject_generator_container__,
    __hydrate_state_update_blocks__,
]

def __prepare_simulation_config__(config: SimulationConfig) -> SimulationConfig:
    return reduce(lambda config, modifier: modifier(config), MODIFIERS, config)
