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
import util


def do(thread_util, sub_task, ):
    unique_id = util.short_unique_id()
    logging.debug('Worker - Starting ID [%s].', str(unique_id))
    logging.info('Worker - Starting to work on SubTask [%s].', str(sub_task.id))
    tasks_to_monitor = []
    for command in sub_task.get_commands():
        process = subprocess.Popen(command, cwd=sub_task.get_parent().wd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   shell=True, preexec_fn=os.setsid)
        logging.debug('Worker - Created process with pid [%s], running [%s].', str(process.pid), str(command))
        thread_util.add_process(sub_task.get_parent().id, process.pid)
        tasks_to_monitor.append((sub_task, process))
    logging.info('Worker - Launched %i process command(s). I\'m done with SubTask [%s].', len(tasks_to_monitor),
                 str(sub_task.id))
    logging.debug('Worker - Finished ID [%s].', str(unique_id))
    return manager.monitor(thread_util, tasks_to_monitor)
