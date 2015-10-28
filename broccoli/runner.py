import shlex
import subprocess
from monitor import Monitor
from collections import deque

"""
    broccoli.Runner
    ~~~~~~~~~~~~~

    Runs tasks.
    Manages the low level subprocess creation.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


class Runner:
    def __init__(self, job):
        self.job = job
        self.tasks = deque([])
        self.add_tasks(job.get_tasks())

    def __run(self):
        tasks_to_monitor = []
        while True:
            try:
                task = self.tasks.popleft()
                command = shlex.split(task.command)
                process = subprocess.Popen(command, stdin=None, stdout=subprocess.PIPE, stderr=None)
                # (stdout, stderr) = process.communicate()
                process.communicate()
                tasks_to_monitor.append((task, process))
            except IndexError:
                break
        monitor = Monitor(self)
        monitor.start(tasks_to_monitor)

    def add_tasks(self, tasks):
        self.tasks.append(tasks)
        self.__run()
