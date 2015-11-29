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
import logging
import multiprocessing
from task import Task


class Job:
    """
       Job constructor

       :param job_config
    """

    def __init__(self, job_config):
        self.id = util.unique_id()
        self.name = job_config.get('jobName')
        self.description = job_config.get('jobDescription')
        self.wd = job_config.get('workingDir')
        self.timeout = job_config.get('timeout')
        self.tasks = [] #multiprocessing.Queue()
        for task_config in job_config.get('tasks'):
            self.tasks.append(Task(task_config))
        logging.info('New Job created: %s', str(self.name))

    """
        Pop Tasks

        :return tasks
    """
    def pop_tasks(self):
        temp = self.tasks
        self.tasks = []
        return temp
