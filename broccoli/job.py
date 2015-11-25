import uuid
import logging
import broccoli.task

"""
    broccoli.Job
    ~~~~~~~~~~~~~

    A Job is a set of tasks working to solve a specific problem.
    The tasks can work together or concurrently.

    See 'broccoli_schema.json' for details on usage.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


class Job:
    """
       Job constructor

       :param name
       :param wd
       :param timeout
    """

    def __init__(self, name='Anonymous', description='', wd='/tmp/', timeout=3600):
        self.id = uuid.uuid4()
        self.name = name
        self.description = description
        self.wd = wd
        self.timeout = timeout
        self.tasks = []

    def __init__(self, jobConfig):
        self.id = uuid.uuid4()
        self.name = jobConfig.get('jobName')
        self.description = jobConfig.get('jobDescription')
        self.wd = jobConfig.get('workingDir')
        self.timeout = jobConfig.get('timeout')
        self.tasks = []
        for taskConfig in jobConfig.get('tasks'):
            self.tasks.append(broccoli.task.Task(taskConfig))
        logging.info('New Job created: %s', str(self.name))


    """
        Pop Tasks

        :return tasks
    """
    def pop_tasks(self):
        temp = self.tasks
        self.tasks = []
        return temp
