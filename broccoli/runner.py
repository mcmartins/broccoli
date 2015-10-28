import shlex
import subprocess
import logging
import signal
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
    # these is a static private variable shared among all instances of the monitor
    # this way we can keep track of everything that is running
    # this is useful to kill running processes when we reach a solution
    __running_processes = []

    def __init__(self, job):
        self.job = job
        self.tasks = deque([])
        self.add_tasks(job.get_tasks())
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(self.job.timeout)

    def __run(self):
        tasks_to_monitor = []
        while True:
            try:
                task = self.tasks.popleft()
                command = shlex.split(task.command)
                process = subprocess.Popen(command, stdin=None, stdout=subprocess.PIPE, stderr=None)
                # (stdout, stderr) = process.communicate()
                process.communicate()
                self.__running_processes.append(process)
                tasks_to_monitor.append((task, process))
                logging.debug('Starting processing the following Task: ' + task)
            except IndexError:
                break
        monitor = Monitor(self)
        monitor.start(tasks_to_monitor)

    def add_tasks(self, tasks):
        self.tasks.append(tasks)
        self.__run()

    def __timeout(self, signum, frame):
        logging.info('Processing timed out...')
        self.__exit_gracefully()

    def __exit_gracefully(self):
        self.__kill_all()
        logging.info('Processing finished...')
        exit(0)

    def __kill_all(self):
        for process in self.__running_processes:
            logging.info('Killing running process: ' + process.id)
            process.kill()
