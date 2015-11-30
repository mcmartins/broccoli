"""
    broccoli.process
    ~~~~~~~~~~~~~



    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import logging
import util
import shlex


class Process(object):
    def __init__(self, parent_task):
        self.parent_task = parent_task
        self.id = util.short_unique_id()
        self.commands = []
        logging.debug('Process - New Process created %s for Task %s', str(self.id), str(self.parent_task.name))
        return

    def add_command(self, command):
        self.__build_commands([command])

    def add_commands(self, commands):
        self.__build_commands(commands)

    def __build_commands(self, commands):
        for command in commands:
            self.commands.append(' '.join(shlex.split(command)))

    def get_commands(self):
        return self.commands

    def get_task(self):
        return self.parent_task

    def __cmp__(self, other):
        return cmp(self.id, other.id)
