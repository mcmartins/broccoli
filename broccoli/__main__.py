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
import json_parser
import thread_util
from job import Job
from task import Task
import logging
import multiprocessing
import os
import signal
from multiprocessing import Pool
from functools import partial

def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if func_name.startswith('__') and not func_name.endswith('__'): #deal with mangled names
        cls_name = cls.__name__.lstrip('_')
        func_name = '_' + cls_name + func_name
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method(func_name, obj, cls):
    for cls in cls.__mro__:
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

import copy_reg
import types
copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(
        description='Main entry point for Broccoli Module. Usage: python -m broccoli -i <input.json>'
    )
    args_parser.add_argument('-v', '--verbose', help='increase output verbosity', action='store_true',
                        required=False)
    args_parser.add_argument('-i', '--input', help='input json file / string', action='store',
                        dest='input', required=True)
    logging.info('Broccoli - Initializing...')
    args = args_parser.parse_args()
    json = json_parser.parse(args.input)
    logger_init(json, args.verbose)
    job = Job(json)
    job.start()
