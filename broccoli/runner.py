"""
    broccoli.Runner
    ~~~~~~~~~~~~~

    Manages the low level subprocess creation.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import os
import logging
import subprocess
import multiprocessing
from monitor import Monitor
from manager import Manager
import atexit


def process(monitor, sub_task):
    tasks_to_monitor = []
    for command in sub_task.get_commands():
        p = subprocess.Popen(command, cwd=sub_task.get_parent().wd, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             shell=True, preexec_fn=os.setsid)
        logging.debug('SubTask - New command running %s with pid %s.', str(command), str(p.pid))
        tasks_to_monitor.append((sub_task, p))
    return monitor.start(tasks_to_monitor)


class Runner:
    def __init__(self, job):
        # change working directory
        os.chdir(job.wd)
        self.job = job
        self.manager = Manager(self.job)
        atexit.register(self.cleanup)
        self.pool = multiprocessing.Pool(multiprocessing.cpu_count())
        logging.info('Runner - Running Tasks for Job: %s.', str(job.name))
        logging.debug('Runner - Working Directory is: %s.', str(job.wd))
        logging.debug('Runner - Will Timeout after: %s seconds.', str(job.timeout))
        self.__run()

    def __run(self):
        import time
        start_time = time.time()
        while True:
            try:
                task = self.manager.tasks.popleft()
                logging.info('Runner - Starting processing Task: %s.', str(task.name))
                sub_tasks = task.get_subtasks()
                for sub_task in sub_tasks:
                    monitor = Monitor(self.manager)
                    self.pool.apply_async(process, args=(monitor, sub_task,))
                logging.warn("--- %s seconds ---" % (time.time() - start_time))
            except IndexError:
                pass

    def cleanup(self):
        self.pool.close()
        logging.info('Runner - Bye Bye.')
