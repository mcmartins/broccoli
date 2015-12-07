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
        self.id = util.short_unique_id()
        self.__parent = parent
        self.name = task_config.get('taskName')
        self.description = task_config.get('taskDescription')
        self.wd = task_config.get('workingDir')
        self.wait = task_config.get('wait')
        self.fail_tolerant = task_config.get('failTolerant')
        self.__preparation = task_config.get('preparation')
        self.__commands = task_config.get('commands')
        self.__children = []
        logging.debug('Task - Created [%s] with ID [%s].', str(self.name), str(self.id))
        logging.debug('Task - Description [%s].', str(self.description))
        children_config = task_config.get('children')
        if children_config:
            for config in children_config:
                self.__children.append(Task(self, config))
        self.sub_tasks = []

    def get_sub_tasks(self):
        # ensure we just process this method once
        if self.sub_tasks:
            return self.sub_tasks
        if self.__preparation:
            pattern = r"{0}".format(urllib.unquote(self.__preparation.get('pattern')))
            # ok, lets see what we can do
            if self.__preparation.get('filterFile'):
                filter_file = self.__preparation.get('filterFile')
                write_file = self.__preparation.get('writeFile')
                placeholder = self.__preparation.get('placeholder')
                copy = self.__preparation.get('copy')
                filter_files_found = [name for name in glob.glob(filter_file)]
                write_files_found = [name for name in glob.glob(write_file)]
                if len(filter_files_found) < 1:
                    raise InvalidFileDirectory('Task - Files were not found matching {0}.'.format(filter_file))
                logging.debug('Task - Found [%s] file(s) to filter using [%s].', str(len(filter_files_found)), str(filter_file))
                if len(write_files_found) < 1:
                    raise InvalidFileDirectory('Task - Files were not found matching {0}.'.format(write_file))
                logging.debug('Task - Found [%s] file(s) to write using [%s].', str(len(write_files_found)), str(write_file))
                # ok, it seems we have a pattern, so we should look inside each file
                if pattern:
                    # look matching regex in each line of a file
                    all_matching_lines = self.__find_in_files(filter_files_found, pattern)
                    logging.debug('Task - Found [%s] matching result(s) using [%s].', str(len(all_matching_lines)), str(pattern))
                    # look matching regex in each line of each file
                    for w_file in write_files_found:
                        for line in filter(None, all_matching_lines):
                            new_file = w_file
                            if copy:
                                # create a copy of the file with the same name plus
                                new_file = self.__create_copy(w_file)
    
                            # get commands to execute
                            self.sub_tasks.append(self.__replace_in_commands(new_file, line))
    
                            # look in side the new file for the placeholder and replace it
                            self.__replace_in_file(new_file, placeholder, line)
                else:
                    # seems you just want to filter files, lets replace them in the commands
                    for f_file in filter_files_found:
                         self.sub_tasks.append(self.__replace_in_commands(f_file, f_file))
            else:
                raise Exception('Task - Oops this shouldn\'t happen!')

        else:
            sub_task = SubTask(self)
            sub_task.add_commands(self.__commands)
            self.sub_tasks.append(sub_task)
        logging.debug('Task - This Task has been splitted in [%s] Sub Task(s).', str(len(self.sub_tasks)))
        return self.sub_tasks

    """
        Utility method to copy files
        
        Returns the file name of the new file copied
    """

    def __create_copy(self, file):
        new_filename = '{0}-{1}-{2}'.format(self.name, util.short_unique_id(), os.path.basename(file))
        shutil.copy2(file, new_filename)
        return new_filename
        
    """
        Utility method to find certain pattern in a set of files
        
        Returns all matching results
    """
    
    def __find_in_files(self, files, pattern):
        all_matching_lines = []
        for file in files:
            with open(file, "r") as f:
                all_matching_lines.extend(re.findall(pattern, f.read(), re.MULTILINE))
                f.close()
        return all_matching_lines
    
    """
        Utility method to generate sub tasks
        
        Returns the new SubTask
    """
    
    def __replace_in_commands(self, file, line=''):
        sub_task = SubTask(self)
        for command in self.__commands:
            # replace placeholder with actual created file
            sub_task.add_command(command.replace('$file', file).replace('$line', line))
        return sub_task
    
    """
        Utility method to replace a placeholder with a value in a file
    """
    
    def __replace_in_file(self, file, placeholder, value):
        # look in side the new file for the placeholder and replace it
        with codecs.open(file, 'r', encoding='utf8') as fr:
            text = fr.read()
            fr.close()
        # replace placeholder
        text = text.replace(placeholder, str(value))
        with codecs.open(file, 'w', encoding='utf8') as fw:
            fw.write(text)
            fw.close()

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

    def __cmp__(self, other):
        return cmp(self.name, other.name)

    def __hash__(self):
        return hash(self.name) ^ hash(self.name)
