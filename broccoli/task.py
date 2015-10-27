import shlex
from collections import deque


class Task:
    """
    This is a Task
    """
    def __init__(self, name='Anonymous', command=''):
        self.parent = None
        self.name = name
        self.command = shlex.split(command)
        self.guidance = deque([])

    def add_guidance(self, task):
        task.parent = self
        self.guidance.append(task)

    def pop_guidance(self):
        return self.guidance.popleft()
