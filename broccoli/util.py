"""
    broccoli.Util
    ~~~~~~~~~~~~~

    Contains Utility methods used within the project

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import os
import signal
import logging
from time import time


"""
    Short unique id generated based on time
    e.g.: short_unique_id() = {str} '83c31574873f'
"""


def short_unique_id():
    return str(hex(int(time() * 999999))[2:])


"""
    Utility method to kill processes
"""


def kill_process(process):
    try:
        os.kill(process, signal.SIGTERM)
        logging.debug('Util - Process with pid [%s] Killed.', str(process))
    except OSError:
        logging.debug('Util - Process with pid [%s] is not present, cannot be killed. Skipping...', str(process))


"""
    Utility method to print output from standard and error
"""


def print_output(std_err, std_out):
    if std_err:
        logging.debug('Util - Standard error (stderr):\n%s', str(std_err))
    if std_out:
        logging.debug('Util - Standard output (stdout):\n%s', str(std_out))


"""
    Utility method to print the tree of tasks executed and finished
"""


def print_task_tree(task):
    def ordinal(n):
        return '%d%s' % (n, 'tsnrhtdd'[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

    tasks = [(task.name, ', '.join([str(sub_task.name) for sub_task in task.get_sub_tasks()]))]
    while task.get_parent() is not None:
        task = task.get_parent()
        tasks.append((task.name, ', '.join([str(sub_task.name) for sub_task in task.get_sub_tasks()])))
    logging.info('Util - The Job finished with the following order:')
    for i, (task, sub) in enumerate(reversed(tasks)):
        logging.info('\t%s - Task: %s', ordinal(i + 1), task)
        logging.info('\t\tSubTask(s): %s', sub)
