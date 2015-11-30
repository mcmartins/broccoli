"""
    broccoli.logging
    ~~~~~~~~~~~~~

    Default logging configuration.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import logging
import os


def initialize(config, verbose):
    # ensure the working directory exists in order to write the log file
    if not os.path.exists(config.get('workingDir')):
        logging.info('The working directory %s specified, does not exist. Creating working directory...', str(config.get('workingDir')))
        os.makedirs(config.get('workingDir'))
    handler = logging.FileHandler(config.get('workingDir') + '/Broccoli-Job-' + config.get('jobName') + '.log')
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
