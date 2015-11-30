"""
    broccoli.SubTask
    ~~~~~~~~~~~~~

    A SubTask is the object that contains the actual work to perform
    Invoking process will run the commands with subprocess.Popen


    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import logging
import util
import shlex
import os
import subprocess


class SubTask:
    def __init__(self, parent_task):
        self.id = util.short_unique_id()
        self.__parent_task = parent_task
        self.__commands = []
        logging.info('Process - New Process created %s for Task %s', str(self.id), str(self.__parent_task.name))
        return

    def add_command(self, command):
        self.__build_commands([command])

    def add_commands(self, commands):
        self.__build_commands(commands)

    def __build_commands(self, commands):
        for command in commands:
            self.__commands.append(' '.join(shlex.split(command)))

    def process(self, monitor):
        tasks_to_monitor = []
        for command in self.__commands:
            logging.debug('Process - New command running %s', str(command))
            process = subprocess.Popen(command, cwd=self.__parent_task.wd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                shell=True, preexec_fn=os.setsid)
            tasks_to_monitor.append((self, process))
        monitor.start(tasks_to_monitor)
        
    def get_parent(self):
        return self.__parent_task

    def __cmp__(self, other):
        return cmp(self.id, other.id)
