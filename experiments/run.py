"""
Executes simulation experiments
"""

import logging
import sys
import time
import pandas as pd

from experiments.default_experiment import experiment
from experiments.post_processing import post_process

# Configure logging framework
# e.g. Use logging.info(...) to log to log file
logger = logging.getLogger()
logger.setLevel(logging.INFO)
# handler = logging.FileHandler(filename=f'logs/experiment-{datetime.now()}.log')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def run(executable=experiment):
    """
    executes experiment
    """
    logging.info("Running experiment")
    start_time = time.time()

    executable.run()

    experiment_duration = time.time() - start_time
    logging.info(f"Experiment complete in {experiment_duration} seconds")

    logging.info("Post-processing results")

    df = pd.DataFrame(executable.results)

    try:
        parameters = executable.simulations[0].model.params
    except:
        parameters = executable.model.params

    df = post_process(df, parameters=parameters)

    post_processing_duration = time.time() - start_time - experiment_duration
    logging.info(f"Post-processing complete in {post_processing_duration} seconds")

    return df, executable.exceptions


if __name__ == '__main__':
    df, _exceptions = run()
    print(df)
