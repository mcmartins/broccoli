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
import sys
from broccoli.runner import Runner

if __name__ == "__main__":
    job = parser.parse(sys.argv[1])
    runner = Runner(job)
    runner.run()
