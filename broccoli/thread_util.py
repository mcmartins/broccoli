"""
    broccoli.ThreadUtil
    ~~~~~~~~~~~~~

    Manages the low level multiprocessing objects.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import multiprocessing

def get_config():
    manager = multiprocessing.Manager()
    config = manager.dict()
    config['clean_exit_0'] = multiprocessing.Event()
    config['clean_exit_1'] = multiprocessing.Event()
    config['clean_exit_2'] = multiprocessing.Event()
    config['clean_exit_5'] = multiprocessing.Event()
    config['running_processes'] = manager.list()
    config['tasks_queue'] = multiprocessing.Queue()
    config['pool'] = multiprocessing.Pool()

    return config
