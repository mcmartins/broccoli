"""
    broccoli.Runner
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
    def __init__(self, job):
        # ensure timeout
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(job.timeout)
        # ensure nothing stays running if the tool blows for some reason
        atexit.register(self.cleanup)
        self.__running_processes = set()
        self.job = job
        self.tasks = deque([])
        self.add_tasks(job.get_tasks())
        logging.debug('Manager - Will Timeout after: %s seconds.', str(job.timeout))

    def kill_process(self, process):
        logging.info('Manager - Killing process %s', str(process))
        try:
            os.kill(process, signal.SIGTERM)
        except OSError:
            logging.info('Manager - Process with pid %s is not present. Skipping...', str(process))

    def add_process(self, process):
        logging.info('Manager - Adding process %s', str(process))
        self.__running_processes.add(process)

    def remove_process(self, process):
        logging.info('Manager - Removing process %s', str(process))
        if process in self.__running_processes:
            self.__running_processes.remove(process)

    def has_running_processes(self):
        return len(self.__running_processes) > 0

    def add_tasks(self, tasks):
        self.tasks.extend(tasks)

    def __timeout(self, signum, frame):
        logging.info('Manager - Processing timed out after %s seconds.', str(self.job.timeout))
        exit(5)

    def cleanup(self):
        # ensure we kill all processes still running
        for process in self.__running_processes:
            self.kill_process(process)
        logging.info('Manager - Bye Bye.')
        exit(0)
