"""
    broccoli.process
    ~~~~~~~~~~~~~



    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import logging


class Process:

    def __init__(self, config):
        self.name = ''
        logging.debug('New Process created %s for Task %s', str(self.name), str(self.name))
