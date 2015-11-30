#!/usr/bin/env python
# coding: utf-8
"""
    broccoli.broccoli
    ~~~~~~~~~~~~~

    This project aims to ease the computation of certain problems by introducing
    tools parallelization and multiprocessing.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import argparse
from logger import initialize as logger_init
from parser import parse
from runner import Runner
from job import Job

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Main entry point for Broccoli Module. Usage: python -m broccoli -i <input.json>'
    )
    parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true',
                        required=False)
    parser.add_argument('-i', '--input', help='input json file / string', action='store',
                        dest='input', required=True)
    args = parser.parse_args()
    config = parse(args.input)
    logger_init(config, args.verbose)
    job = Job(config)
    Runner(job)
