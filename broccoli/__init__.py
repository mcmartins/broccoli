#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

"""
    broccoli.__init___
    ~~~~~~~~~~~~~

    Initialize module with default logging config.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

__version__ = '0.0.2'

logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.INFO)
