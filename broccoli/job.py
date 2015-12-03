"""
    broccoli.Job
    ~~~~~~~~~~~~~

    A Job is a set of tasks working to solve a specific problem.
    The tasks can work together or concurrently.

    See 'broccoli_schema.json' for details on usage.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import util
import time
import logging
from task import Task
import worker
import multiprocessing
import new_monitor
import Queue


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
        logging.info('New Job created: %s', str(self.name))
        for task_config in job_config.get('tasks'):
            # TODO chouldn't the parent be the Job!?
            self.__tasks.append(Task(None, task_config))

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
        logging.info('Job - Starting processing Job: %s.', str(self.name))
        logging.info('Job - Sending Tasks to Processing Queue.')
        tasks_queue = multiprocessing.Queue()
        pool = multiprocessing.Pool()
        kill = multiprocessing.Event()
        thread = (tasks_queue, pool, kill)
        for task in self.__tasks:
            tasks_queue.put(task)
        # runs while none of the threads notify to stop with an exit code
        while not kill.is_set():
            try:
                task = tasks_queue.get()
                logging.info('Job - Starting processing Task: %s.', str(task.name))
                sub_tasks = task.get_sub_tasks()
                for sub_task in sub_tasks:
                    #worker.do(thread, sub_task)
                    pool.apply_async(worker.do, args=(thread, sub_task, ))
            except Queue.Empty:
                # seems nothing is the queue for now
                time.sleep(1)
                pass
