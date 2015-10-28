import uuid

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

    def __init__(self, name='Anonymous', wd='/tmp/', timeout=3600):
        self.id = uuid.uuid4()
        self.name = name
        self.wd = wd
        self.timeout = timeout
        self.tasks = []

    """
        Add Tasks to the Job

        :param task
    """

    def add_task(self, task):
        self.tasks.append(task)

    """
        Pop Tasks

        :return tasks
    """
    def pop_tasks(self):
        temp = self.tasks
        self.tasks = []
        return temp
