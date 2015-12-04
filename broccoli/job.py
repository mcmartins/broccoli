"""
    broccoli.Job
    ~~~~~~~~~~~~~

    A Job is a set of tasks working to solve a specific problem.
    The tasks can work together or concurrently.

    See 'broccoli_schema.json' for details on Job Structure.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import util
import time
import logging
import multiprocessing
import Queue
import atexit
import os
import signal
from task import Task
import worker


class Job:
    """
       Job constructor

       :param job_config
    """

    def __init__(self, job_config):
        self.__id = util.short_unique_id()
        self.name = job_config.get('jobName')
        self.description = job_config.get('jobDescription')
        self.wd = job_config.get('workingDir')
        self.timeout = job_config.get('timeout')
        self.__tasks = []
        logging.debug('Job - Created [%s] with ID [%s].', str(self.name), str(self.__id))
        for task_config in job_config.get('tasks'):
            self.__tasks.append(Task(None, task_config))
        # change working directory
        os.chdir(self.wd)
        # ensure timeout
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(self.timeout)
        # ensure nothing stays running if the tool blows for some reason
        atexit.register(self.__cleanup)
        logging.debug('Job - Initializing a Processing Pool with [%s] cores.', str(multiprocessing.cpu_count()))
        self.multiprocessing_manager = multiprocessing.Manager()
        self.tasks_queue = self.multiprocessing_manager.Queue()
        self.running_processes = self.multiprocessing_manager.list()
        self.pool = multiprocessing.Pool()
        self.kill_event = self.multiprocessing_manager.Event()
        self.thread_utils = (self.tasks_queue, self.running_processes, self.kill_event)

    """
        Get Tasks

        :return tasks
    """

    def get_tasks(self):
        return self.__tasks

    """
        Start the Job
    """

    def start(self):
        logging.info('Job - Starting Job [%s].', str(self.name))
        logging.info('Job - Sending Tasks to Processing Queue.')
        for task in self.__tasks:
            self.thread_utils[0].put(task)
        # runs while none of the threads notify to stop with an exit code
        while not self.thread_utils[2].is_set():
            try:
                task = self.thread_utils[0].get_nowait()
                logging.info('Job - Starting processing Task [%s].', str(task.name))
                sub_tasks = task.get_sub_tasks()
                for sub_task in sub_tasks:
                    self.pool.apply_async(worker.do, args=(self.thread_utils, sub_task,))
            except Queue.Empty:
                # seems nothing is the queue for now
                time.sleep(1)
                pass

    def __timeout(self, signum, frame):
        logging.info('Job - Processing timed out after %s seconds.', str(self.timeout))
        exit(5)

    def __cleanup(self):
        logging.info('Job - Cleaning up all processes.')
        for process in self.thread_utils[1]:
            util.kill_process(process)
        logging.debug('Job - Closing Processing Pool.')
        self.pool.close()
        logging.info('Job - Bye Bye.')
