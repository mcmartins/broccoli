from broccoli.task import Task

"""
    broccoli.Task
    ~~~~~~~~~~~~~

    A Task is a process that runs in the background.
    A Task can have Sub Tasks (Guidance).
    All Sub Tasks (Guidance's) have a parent assigned.
    A Task is considered finished when all Sub Tasks (Guidance's) are finished.

    See 'broccoli_schema.json' for details on usage.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


class StrictTask(Task):
    """
       Task constructor

       :param name
       :param command
       :param wait
    """

    def __init__(self, name='Anonymous', command='', wait=False):
        Task.__init__(self, name, command)
        self.wait = wait
