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
from collections import deque

from monitor import Monitor
from worker import Worker


class Runner:
    # this is a static private variable shared among all instances of the monitor
    # this way we can keep track of everything that is running
    # this is useful to kill running processes when we reach a solution
    _running_processes = []
    _workers = []

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
        self.work_queue = multiprocessing.Queue()
        logging.info('Runner - Running Tasks for Job: %s.', str(job.name))
        logging.debug('Runner - Working Directory is: %s.', str(job.wd))
        logging.debug('Runner - Will Timeout after: %s seconds.', str(job.timeout))
        #for i in range(multiprocessing.cpu_count()):
        #    Runner._workers.append(Worker(self.job, self.work_queue, self))
        #    Runner._workers[i].start()
        self.add_tasks(job.get_tasks())

    def __run(self):
        while True:
            try:
                task = self.tasks.popleft()
                logging.info('Runner - Starting processing Task: %s.', str(task.name))
                sub_tasks = task.get_subtasks()
                for sub_task in sub_tasks:
                    #self.work_queue.put(sub_task)
                    jobs = []
                    for i in range(0, 2):
                        out_list = list()
                        monitor = Monitor(self)
                        thread = threading.Thread(target=sub_task.process(monitor))
                        jobs.append(thread)

                    # Start the threads (i.e. calculate the random number lists)
                    for j in jobs:
                        j.start()

                    # Ensure all of the threads have finished
                    for j in jobs:
                        j.join()
            except IndexError:
                break

    def add_tasks(self, tasks):
        self.tasks.extend(tasks)
        self.__run()
        
    def kill_process(self, (sub_task, process)):
        logging.info('Runner - Killing process %s', str(process.pid))
        os.killpg(process.pid, signal.SIGTERM)
        self.remove_process((sub_task, process))

    def add_processes(self, tuple):
        self._running_processes.extend(tuple)

    def remove_process(self, (sub_task, process)):
        self._running_processes.remove((sub_task, process))
        
    def has_running_processes(self):
        return len(self._running_processes) > 0

    def __timeout(self, signum, frame):
        logging.info('Runner - Processing timed out after %s seconds.', str(self.job.timeout))
        exit(5)

    def cleanup(self):
        for process in Runner._running_processes:
            logging.info('Runner - Killing running process with pid %s.', str(process.pid))
            os.killpg(process.pid, signal.SIGTERM)
        #for worker in Runner._workers:
        #    logging.info('Runner - Killing running worker with id %s.', str(worker.id))
        #    worker.kill()
        logging.info('Runner - Bye Bye.')
