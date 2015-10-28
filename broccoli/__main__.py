#!/usr/bin/env python
# coding: utf-8
"""
    broccoli.broccoli
    ~~~~~~~~~~~~~

    This project aims to ease the computation of certain problems by introducing
    tools parallelization and multithreading.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import argparse
import broccoli.logger
import broccoli.runner
import broccoli.parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Main entry point for Broccoli Module. Usage: python broccoli -i <input.json>'
    )
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true',
                        required=False)
    parser.add_argument('-i', '--input', help='input json file / string', action='store',
                        dest='input', required=True)
    args = parser.parse_args()
    job = broccoli.parser.parse(args.input)
    broccoli.logger.initialize(job, args.verbose)
    broccoli.runner.Runner(job)
