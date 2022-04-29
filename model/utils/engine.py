"""
radCAD Engine extension to give us more control over how simulations happen
"""
import copy
from radcad.engine import Engine as RadCadEngine
from radcad import core, wrappers

from .generator_container import GENERATOR_CONTAINER_PARAM_KEY, GeneratorContainer

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
                        params_for_run = __inject_generator_container__(param_set)
                        state_update_blocks_for_run = __hydrate_state_update_blocks__(
                            state_update_blocks,
                            params_for_run)
                        yield wrappers.RunArgs(
                            simulation_index,
                            timesteps,
                            run_index,
                            subset_index,
                            copy.deepcopy(initial_state),
                            state_update_blocks_for_run,
                            params_for_run,
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

                    params_for_run = __inject_generator_container__(param_set)
                    state_update_blocks_for_run = __hydrate_state_update_blocks__(
                        state_update_blocks,
                        params_for_run)

                    yield wrappers.RunArgs(
                        simulation_index,
                        timesteps,
                        run_index,
                        0,
                        copy.deepcopy(initial_state),
                        state_update_blocks_for_run,
                        params_for_run,
                        self.deepcopy,
                        self.drop_substeps,
                    )
                    self.executable._after_subset(context=context)
                    self.executable._after_run(context=context)

            self.executable._after_simulation(
                simulation=simulation
            )

def __inject_generator_container__(_params):
    params = copy.deepcopy(_params)
    params.update({
        GENERATOR_CONTAINER_PARAM_KEY: GeneratorContainer(params)
    })
    return params

def __hydrate_state_update_blocks__(state_update_blocks, params):
    container = params.get(GENERATOR_CONTAINER_PARAM_KEY)
    flat_state_update_blocks = []
    for state_update_block in state_update_blocks:
        if state_update_block.get('type') == 'dynamic':
            generator = container.get(state_update_block.get('source'))
            flat_state_update_blocks += generator.state_update_blocks()
        else:
            flat_state_update_blocks += [state_update_block]
    return flat_state_update_blocks
