import logging
import os

"""
    broccoli.logging
    ~~~~~~~~~~~~~

    Default logging configuration.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


def initialize(job, verbose):
    # ensure the working directory exists in order to write the log file
    if not os.path.exists(job.wd):
        logging.info('The working directory %s specified, does not exist. Creating working directory...', job.wd)
        os.makedirs(job.wd)
    handler = logging.FileHandler(job.wd + '/Broccoli-Job-' + str(job.id) + '.log')
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
