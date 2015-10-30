import os
import pipes
import shlex
import atexit
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
    # this is a static private variable shared among all instances of the monitor
    # this way we can keep track of everything that is running
    # this is useful to kill running processes when we reach a solution
    running_processes = []

    @staticmethod
    def terminate():
        for process in Runner.running_processes:
            logging.info('Killing running process with pid %s.', str(process.pid))
            os.killpg(process.pid, signal.SIGTERM)
        logging.info('Bye Bye.')

    def __init__(self, job):
        # change working directory
        os.chdir(job.wd)
        # ensure timeout
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(job.timeout)
        # ensure nothing stays running if the tool blows for some reason
        atexit.register(Runner.terminate)
        self.job = job
        self.tasks = deque([])
        logging.info('Runner - Running Tasks for Job: %s', str(job.name))
        logging.debug('Runner - Working Directory is: %s', str(job.wd))
        logging.debug('Runner - Will Timeout after: %s seconds', str(job.timeout))
        self.add_tasks(job.pop_tasks())

    def __run(self):
        tasks_to_monitor = []
        while True:
            try:
                task = self.tasks.popleft()
                logging.info('Runner - Starting processing Task: %s', str(task.name))
                # TODO Implement the proper way - https://security.openstack.org/guidelines/dg_avoid-shell-true.html
                # TODO Sanitize all input values
                # TODO allow piping tasks to sub tasks
                command = ' '.join(shlex.split(task.command))
                logging.debug('Runner - Task Command: %s', str(command))
                process = subprocess.Popen(command, cwd=self.job.wd, stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                           shell=True, preexec_fn=os.setsid)
                Runner.running_processes.append(process)
                tasks_to_monitor.append((task, process))
            except IndexError:
                break
        monitor = Monitor(self)
        monitor.start(tasks_to_monitor)

    def add_tasks(self, tasks):
        self.tasks.extend(tasks)
        self.__run()

    def __timeout(self, signum, frame):
        logging.info('Processing timed out after %s seconds.', str(self.job.timeout))
        exit(5)

    def __run_safe(self, command):
        # TODO redo this code and replace __run function
        if "|" in command:
            cmd_parts = command.split('|')
        else:
            cmd_parts = [command]
        i = 0
        p = {}
        for cmd_part in cmd_parts:
            cmd_part = cmd_part.strip()
            if i == 0:
                p[i] = subprocess.Popen(pipes.quote(cmd_part), stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            else:
                p[i] = subprocess.Popen(pipes.quote(cmd_part), stdin=p[i - 1].stdout, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            i += 1
