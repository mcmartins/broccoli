"""
    broccoli.Task
    ~~~~~~~~~~~~~

    A Task is a specific work to be done.
    A Task can have Children. Children has a parent assigned.
    A Task is considered finished when all children is finished.
    Tasks commands are breakdown in Sub Tasks.

    See 'broccoli_schema.json' for details on usage.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import util
import logging
import re
import codecs
import shutil
import glob
import os
import urllib
from sub_task import SubTask


class InvalidFileDirectory(Exception):
    """
    Raised when the the user tries to use a file or directory that we cannot find

    Attributes:
        message  --
    """

    def __init__(self, message):
        self.message = 'Cannot find the file/directory specified. ' + message

    def __str__(self):
        return repr(self.message)


class Task:
    """
       Task constructor

       :param task_config
    """

    def __init__(self, parent, task_config):
        self.__id = util.short_unique_id()
        self.__parent = parent
        self.name = task_config.get('taskName')
        self.description = task_config.get('taskDescription')
        self.wd = task_config.get('workingDir')
        self.wait = task_config.get('wait')
        self.__preparation = task_config.get('preparation')
        self.__commands = task_config.get('commands')
        self.__children = []
        logging.debug('Task - Created [%s] with ID [%s].', str(self.name), str(self.__id))
        children_config = task_config.get('children')
        if children_config:
            for config in children_config:
                self.__children.append(Task(self, config))
        self.sub_tasks = []

    def get_sub_tasks(self):\
        # ensure we just process this method once
        if self.sub_tasks:
            return self.sub_tasks
        if self.__preparation:
            pattern = r"{0}".format(urllib.unquote(self.__preparation.get('pattern')))
            # ok, lets see what we can do
            # did you select search files in dir or lines in file?
            if self.__preparation.get('filterFile'):
                filter_file = self.__preparation.get('filterFile')
                write_file = self.__preparation.get('writeFile')
                placeholder = self.__preparation.get('placeholder')
                copy = self.__preparation.get('copy')
                filter_files_found = [name for name in glob.glob(filter_file)]
                write_files_found = [name for name in glob.glob(write_file)]
                if len(filter_files_found) < 1:
                    raise InvalidFileDirectory('Task - Files were not found matching {0}.'.format(filter_file))
                if len(write_files_found) < 1:
                    raise InvalidFileDirectory('Task - Files were not found matching {0}.'.format(write_file))
                # look matching regex in each line of a file
                all_matching_lines = []
                for f_file in filter_files_found:
                    with open(f_file, "r") as f:
                        all_matching_lines.extend(re.findall(pattern, f.read(), re.MULTILINE))
                        f.close()

                # look matching regex in each line of each file
                for w_file in write_files_found:
                    for line in filter(None, all_matching_lines):
                        new_file = w_file
                        if copy:
                            # create a copy of the file with the same name plus
                            new_file = \
                                '{0}-{1}-{2}'.format(self.name, util.short_unique_id(),
                                                     os.path.basename(w_file))
                            shutil.copy2(w_file, new_file)

                        # get commands to execute
                        sub_task = SubTask(self)
                        for command in self.__commands:
                            # replace placeholder with actual created file
                            sub_task.add_command(command.replace('$file', new_file).replace('$line', line))
                        self.sub_tasks.append(sub_task)

                        # look in side the new file for the placeholder and replace it
                        with codecs.open(new_file, 'r', encoding='utf8') as fw:
                            text = fw.read()
                            fw.close()
                        text = text.replace(placeholder, str(line))
                        with codecs.open(new_file, 'w', encoding='utf8') as fw:
                            fw.write(text)
                            fw.close()

            else:
                raise Exception('Task - Oops this shouldn\'t happen!')

        else:
            sub_task = SubTask(self)
            sub_task.add_commands(self.__commands)
            self.sub_tasks.append(sub_task)

        return self.sub_tasks

    """
        Get Guidance Tasks

        :return tasks
    """

    def get_children(self):
        return self.__children

    """
        Returns True if there are Guidance Tasks
    """

    def has_children(self):
        return len(self.__children) > 0

    """
        Returns the parent task if this task is a child, otherwise None
    """

    def get_parent(self):
        return self.__parent
