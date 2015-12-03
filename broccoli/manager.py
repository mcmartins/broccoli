"""
    broccoli.Manager
    ~~~~~~~~~~~~~

    Manages the low level subprocess creation.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import os
import atexit
import logging
import signal
from collections import deque


class Manager:

    __running_processes = set()
    __tasks = deque([])

    def __init__(self, job):
        # ensure timeout
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(job.timeout)
        # ensure nothing stays running if the tool blows for some reason
        atexit.register(self.cleanup)
        self.job = job
        self.add_tasks(job.get_tasks())
        logging.debug('Manager - Will Timeout after: %s seconds.', str(job.timeout))

    @staticmethod
    def add_process(process):
        logging.info('Manager - Adding process %s', str(process))
        Manager.__running_processes.add(process)

    @staticmethod
    def remove_process(process):
        logging.info('Manager - Removing process %s', str(process))
        if process in Manager.__running_processes:
            Manager.__running_processes.remove(process)

    @staticmethod
    def kill_process(process):
        logging.info('Manager - Killing process %s', str(process))
        try:
            os.kill(process, signal.SIGTERM)
        except OSError:
            logging.info('Manager - Process with pid %s is not present. Skipping...', str(process))

    @staticmethod
    def has_running_processes():
        return len(Manager.__running_processes) > 0

    @staticmethod
    def add_tasks(tasks):
        Manager.__tasks.extend(tasks)

    @staticmethod
    def get_task():
        return Manager.__tasks.popleft()

    def __timeout(self, signum, frame):
        logging.info('Manager - Processing timed out after %s seconds.', str(self.job.timeout))
        exit(5)

    def cleanup(self):
        # ensure we kill all processes still running
        for process in self.__running_processes:
            self.kill_process(process)
        exit(0)
        logging.info('Manager - Bye Bye.')
