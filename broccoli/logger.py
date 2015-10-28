import logging

"""
    broccoli.logging
    ~~~~~~~~~~~~~

    Default logging configuration.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


def initialize(job, verbose):
    handler = logging.FileHandler(job.wd + '/Broccoli-Job-' + str(job.id) + '.log')
    formatter = logging.Formatter('%(asctime)s - [%(levelname)s] - %(message)s')
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
