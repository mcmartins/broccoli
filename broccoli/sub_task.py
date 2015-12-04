"""
    broccoli.SubTask
    ~~~~~~~~~~~~~

    A SubTask is the actual work to perform.
    Contains the commands to run with subprocess.Popen

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import logging
import util
import shlex


class SubTask:
    def __init__(self, parent_task):
        self.id = util.short_unique_id()
        self.name = self.id
        self.__parent_task = parent_task
        self.__commands = []
        logging.info('SubTask - Created ID [%s] for Task [%s].', str(self.name), str(self.__parent_task.name))

    def add_command(self, command):
        self.__build_commands([command])

    def add_commands(self, commands):
        self.__build_commands(commands)

    def __build_commands(self, commands):
        for command in commands:
            self.__commands.append(' '.join(shlex.split(command)))

    def get_commands(self):
        return self.__commands

    def get_parent(self):
        return self.__parent_task

    def __cmp__(self, other):
        return cmp(self.id, other.id)
