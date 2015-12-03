"""
    broccoli.Worker
    ~~~~~~~~~~~~~

    A Worker is responsible for process Sub Tasks

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import logging
import subprocess
import os
from monitor import Monitor


def do(task, queue):
    logging.info('Worker - Started Task: %s.', str(task.name))
    tasks_to_monitor = []
    sub_tasks = task.get_sub_tasks()
    for sub_task in sub_tasks:
        for command in sub_task.get_commands():
            p = subprocess.Popen(command, cwd=sub_task.get_parent().wd, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=True, preexec_fn=os.setsid)
            logging.debug('Worker - Process with pid %s is running command %s.',  str(p.pid), str(command))
            tasks_to_monitor.append((sub_task, p))
        Monitor(tasks_to_monitor).monitor(queue)

    logging.info('Worker - We\'re done with SubTask %s. Launched %i command(s).', str(task.name), len(tasks_to_monitor))
