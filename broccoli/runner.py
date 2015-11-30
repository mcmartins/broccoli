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
from collections import deque
from worker import Worker


class Runner:
    # this is a static private variable shared among all instances of the monitor
    # this way we can keep track of everything that is running
    # this is useful to kill running processes when we reach a solution
    __running_processes = []
    __workers = []

    @staticmethod
    def terminate():
        for process in Runner.__running_processes:
            logging.info('Runner - Killing running process with pid %s.', str(process.pid))
            os.killpg(process.pid, signal.SIGTERM)
        for worker in Runner.__workers:
            logging.info('Runner - Killing running worker with id %s.', str(worker.id))
            worker.kill()
        logging.info('Runner - Bye Bye.')

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
        logging.info('Runner - Running Tasks for Job: %s.', str(job.name))
        logging.debug('Runner - Working Directory is: %s.', str(job.wd))
        logging.debug('Runner - Will Timeout after: %s seconds.', str(job.timeout))
        for i in range(multiprocessing.cpu_count()):
            Runner.__workers.append(Worker(self.job, self.work_queue, self))
            Runner.__workers[i].start()
        self.add_tasks(job.get_tasks())

    def __run(self):
        while True:
            try:
                task = self.tasks.popleft()
                logging.info('Runner - Starting processing Task: %s.', str(task.name))
                sub_tasks = task.get_subtasks()
                for sub_task in sub_tasks:
                    self.work_queue.put(sub_task)
            except IndexError:
                break

    def add_tasks(self, tasks):
        self.tasks.extend(tasks)
        self.__run()
        
    def kill_process(self, process):
        logging.info('Runner - Killing process %s', str(process.pid))
        os.killpg(process.pid, signal.SIGTERM)
        
    def has_running_processes(self):
        return len(self.__running_processes) > 0

    def __timeout(self, signum, frame):
        logging.info('Runner - Processing timed out after %s seconds.', str(self.job.timeout))
        exit(5)
