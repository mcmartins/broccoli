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
from threading_manager import ThreadingManager
from threading_manager import ThreadingProperties
import atexit
import os
import signal
import Queue
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
        logging.debug('Job - Will run in the following Working Directory [%s].', str(self.wd))
        # ensure timeout
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(self.timeout)
        # ensure nothing stays running if the tool blows for some reason
        atexit.register(self.__cleanup)
        self.multiprocessing_manager = ThreadingManager()
        self.multiprocessing_manager.start()
        self.pool = multiprocessing.Pool()
        self.thread_utils = self.multiprocessing_manager.ThreadingProperties()
        logging.debug('Job - Initializing a Processing Pool with [%s] cores.', str(multiprocessing.cpu_count()))

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
            self.thread_utils.add_task(task)
        # runs while none of the threads notify to stop with an exit code
        while not self.thread_utils.is_kill_event_set():
            try:
                task = self.thread_utils.get_task()
                logging.info('Job - Starting processing Task [%s].', str(task.name))
                sub_tasks = task.get_sub_tasks()
                for sub_task in sub_tasks:
                    worker.do(self.thread_utils, sub_task,)
                    #self.pool.apply_async(worker.do, args=(self.thread_utils, sub_task,))
            except Queue.Empty:
                # seems nothing is the queue for now
                time.sleep(1)
                pass
        exit(self.thread_utils.get_result_code())

    def __timeout(self, signum, frame):
        logging.info('Job - Processing timed out after %s seconds.', str(self.timeout))
        exit(5)

    def __cleanup(self):
        logging.debug('Job - Closing Processing Pool.')
        self.pool.close()
        logging.info('Job - Bye Bye.')
