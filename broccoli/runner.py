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
import multiprocessing
import threading
from multiprocessing import Pool as ThreadPool 
from multiprocessing import Array
from collections import deque

from monitor import Monitor
from worker import Worker


class Runner:

    def __init__(self, job):
        # change working directory
        os.chdir(job.wd)
        # ensure timeout
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(job.timeout)
        # ensure nothing stays running if the tool blows for some reason
        atexit.register(self.cleanup)
        self.job = job
        self.tasks = deque([])
        # this is a static private variable shared among all instances of the monitor
        # this way we can keep track of everything that is running
        # this is useful to kill running processes when we reach a solution
        self._running_processes = []
        self.pool = ThreadPool(multiprocessing.cpu_count())
        logging.info('Runner - Running Tasks for Job: %s.', str(job.name))
        logging.debug('Runner - Working Directory is: %s.', str(job.wd))
        logging.debug('Runner - Will Timeout after: %s seconds.', str(job.timeout))
        self.add_tasks(job.get_tasks())
        self.__run()

    def __run(self):
        while True:
            try:
                task = self.tasks.popleft()
                logging.info('Runner - Starting processing Task: %s.', str(task.name))
                sub_tasks = task.get_subtasks()
                for sub_task in sub_tasks:
                    monitor = Monitor(self)
                    self.pool.apply_async(sub_task.process(monitor))
                #self.pool.close()
                #self.pool.join()
            except IndexError:
                pass

    def add_tasks(self, tasks):
        self.tasks.extend(tasks)
        
    def kill_process(self, process):
        logging.info('Runner - Killing process %s', str(process))
        self.remove_process(process)
        try:
            os.kill(process, signal.SIGTERM)
        except OSError:
            logging.info('Runner - Process with pid %s is not present. Skipping...', str(process))

    def add_process(self, process):
        logging.info('Runner - Adding process %s', str(process))
        self._running_processes.append(process)

    def remove_process(self, process):
        logging.info('Runner - Removing process %s', str(process))
        self._running_processes.remove(process)
        
    def has_running_processes(self):
        return len(self._running_processes) > 0

    def __timeout(self, signum, frame):
        logging.info('Runner - Processing timed out after %s seconds.', str(self.job.timeout))
        exit(5)

    def cleanup(self):
        # ensure we kill all processes still running
        for process in self._running_processes:
            self.kill_process(process)
        # close the pool
        self.pool.close()
        logging.info('Runner - Bye Bye.')
