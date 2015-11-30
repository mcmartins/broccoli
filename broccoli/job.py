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
from task import Task


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
        self.tasks = []
        for task_config in job_config.get('tasks'):

            self.tasks.append(Task(None, task_config))
        logging.info('New Job created: %s', str(self.name))

    """
        Get Tasks

        :return tasks
    """

    def get_tasks(self):
        # temp = self.tasks
        # self.tasks = []
        return self.tasks
