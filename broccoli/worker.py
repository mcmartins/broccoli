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
import manager


def do(thread_util, sub_task,):
    logging.info('Worker - Started SubTask: %s.', str(sub_task.id))
    tasks_to_monitor = []
    for command in sub_task.get_commands():
        p = subprocess.Popen(command, cwd=sub_task.get_parent().wd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=True, preexec_fn=os.setsid)
        logging.debug('Worker - Process with pid %s is running command %s.', str(p.pid), str(command))
        thread_util[1].append(p.pid)
        tasks_to_monitor.append((sub_task, p))
    manager.monitor(thread_util, tasks_to_monitor)
    logging.info('Worker - We\'re done with SubTask %s. Launched %i command(s).', str(sub_task.id),
                 len(tasks_to_monitor))
