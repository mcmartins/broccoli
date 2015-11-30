import os
import atexit
import logging
import signal
import multiprocessing
from collections import deque
from worker import Worker

"""
    broccoli.Runner
    ~~~~~~~~~~~~~

    Runs tasks.
    Manages the low level subprocess creation.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


class Runner:
    # this is a static private variable shared among all instances of the monitor
    # this way we can keep track of everything that is running
    # this is useful to kill running processes when we reach a solution
    running_processes = []

    @staticmethod
    def terminate():
        for process in Runner.running_processes:
            logging.info('Killing running process with pid %s.', str(process.pid))
            os.killpg(process.pid, signal.SIGTERM)
        logging.info('Bye Bye.')

    def __init__(self, job):
        # change working directory
        os.chdir(job.wd)
        # ensure timeout
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(job.timeout)
        # ensure nothing stays running if the tool blows for some reason
        atexit.register(Runner.terminate)
        self.job = job
        self.tasks = deque([])
        self.work_queue = multiprocessing.Queue()
        logging.info('Runner - Running Tasks for Job: %s', str(job.name))
        logging.debug('Runner - Working Directory is: %s', str(job.wd))
        logging.debug('Runner - Will Timeout after: %s seconds', str(job.timeout))
        for i in range(multiprocessing.cpu_count()):
            Worker(self.job, self.work_queue, self).start()
            self.work_queue.put(None)
        self.add_tasks(job.get_tasks())

    def __run(self):
        while True:
            try:
                task = self.tasks.popleft()
                self.work_queue.put(task.prepare())
                logging.info('Runner - Starting processing Task: %s', str(task.name))
            except IndexError:
                break

    def add_tasks(self, tasks):
        self.tasks.extend(tasks)
        self.__run()

    def __timeout(self, signum, frame):
        logging.info('Processing timed out after %s seconds.', str(self.job.timeout))
        exit(5)
