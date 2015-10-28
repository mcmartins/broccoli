import logging

"""
    broccoli.logging
    ~~~~~~~~~~~~~

    Default logging configuration.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""
logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.INFO)
