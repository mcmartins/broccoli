import logging

"""
    broccoli.logger
    ~~~~~~~~~~~~~

    Logging configuration.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


def main(job_name):
    logging.basicConfig(format='[%(levelname)s] - %(asctime)s: %(message)s',
                        filename='Broccoli-Job-' + job_name + '.log', level=logging.DEBUG)
    logging.info('Started')
