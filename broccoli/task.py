from collections import deque
import uuid

"""
    broccoli.Task
    ~~~~~~~~~~~~~

    A Task is a process that runs in the background.
    A Task can have Sub Tasks (Guidance).
    All Sub Tasks (Guidances) have a parent assigned.
    A Task is considered finished when all Sub Tasks (Guindances) are finished.

    See 'broccoli_schema.json' for details on usage.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


class Task:
    """
       Task constructor

       :param name
       :param command
       :param wait
    """

    def __init__(self, name='Anonymous', command='', wait=False):
        self.id = uuid.uuid4()
        self.parent = None
        self.name = name
        self.command = command
        self.wait = wait
        self.guidance = deque([])

    """
        Add Sub Task (Guidance)

        :param task
    """

    def add_guidance(self, task):
        task.parent = self
        self.guidance.append(task)

    """
        Get next Sub Task (Guidance) in the queue

        :return task
    """

    def pop_guidance(self):
        return self.guidance.popleft()

    """
        Get Sub Tasks (Guidance) in the queue

        :return tasks
    """

    def get_guidance(self):
        return self.guidance
