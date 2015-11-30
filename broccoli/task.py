"""
    broccoli.Task
    ~~~~~~~~~~~~~

    A Task is a process that runs in the background.
    A Task can have Sub Tasks (Guidance).
    All Sub Tasks (Guidance's) have a parent assigned.
    A Task is considered finished when all Sub Tasks (Guidance's) are finished.

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
        logging.debug('New Task created: %s', str(self.name))
        children_config = task_config.get('children')
        if children_config:
            for config in children_config:
                self.__children.append(Task(self, config))

    def get_subtasks(self):
        sub_tasks = []
        if self.__preparation:
            pattern = r"{0}".format(urllib.unquote(self.__preparation.get('pattern')))
            # ok, lets see what we can do
            # did you select search files in dir or lines in file?
            if self.__preparation.get('filterFile'):
                filter_file = self.__preparation.get('filterFile')
                write_file = self.__preparation.get('writeFile')
                placeholder = self.__preparation.get('placeholder')
                copy = self.__preparation.get('copy')
                if os.path.exists(filter_file):
                    # look matching regex in each line of a file
                    with open(filter_file, "r") as f:
                        all_matching_lines = re.findall(pattern, f.read(), re.MULTILINE)
                        f.close()

                        # create a copy of the file with the same name plus
                        for line in filter(None, all_matching_lines):
                            new_file = write_file
                            if copy:
                                new_file = \
                                    '{0}-{1}-{2}'.format(self.name, util.short_unique_id(),
                                                         os.path.basename(write_file))
                                shutil.copy2(write_file, new_file)

                            # get commands to execute
                            sub_task = SubTask(self)
                            for command in self.__commands:
                                # replace placeholder with actual created file
                                sub_task.add_command(command.replace('$file', new_file).replace('$line', line))
                            sub_tasks.append(sub_task)

                            # look in side the new file for the placeholder and replace it
                            with codecs.open(new_file, 'rw+', encoding='utf8') as fw:
                                text = fw.read()
                                fw.seek(0)
                                fw.write(text.replace(placeholder, str(line)))
                                fw.close()

                else:
                    raise Exception('File does not exist!')

            elif self.__preparation.get('searchDirectory'):
                search_directory = self.__preparation.get('searchDirectory')
                if os.path.exists(search_directory):
                    # look for files matching the regex in a dir
                    all_matching_files = [name for name in glob.glob(os.path.join(search_directory, pattern))]

                    for match_file in all_matching_files:
                        # replace placeholder with matching file
                        sub_task = SubTask(self)
                        for command in self.__commands:
                            sub_task.add_command(command.replace('$file', match_file))
                        sub_tasks.append(sub_task)

                else:
                    raise Exception('Directory does not exist!')
                    
            else:
                raise Exception('Oops this shouldn\'t happen!')
                
        else:
            sub_task = SubTask(self)
            sub_task.add_commands(self.__commands)
            sub_tasks.append(sub_task)

        return sub_tasks

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
