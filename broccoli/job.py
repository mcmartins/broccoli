from collections import deque


class Job:
    """
    This is a Job
    """
    def __init__(self, name='Anonymous', wd='/tmp/', timeout=3600):
        self.name = name
        self.wd = wd
        self.timeout = timeout
        self.tasks = deque([])

    def add_task(self, task):
        self.tasks.append(task)

    def pop_task(self):
        self.tasks.popleft()
