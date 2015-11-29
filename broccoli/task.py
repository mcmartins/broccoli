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
import multiprocessing
import re
import codecs
import shutil
import glob
import os
import urllib


class Task:
    """
       Task constructor

       :param task_config
    """

    def __init__(self, task_config):
        self.id = util.unique_id()
        self.name = task_config.get('taskName')
        self.description = task_config.get('taskDescription')
        self.wait = task_config.get('wait')
        self.preparation = task_config.get('preparation')
        self.commands = task_config.get('commands')
        self.guidance = []  # multiprocessing.Queue()
        guidance_config = task_config.get('guidance')
        if guidance_config:
            for config in guidance_config:
                self.guidance.append(Task(config))
        logging.debug('New Task created: %s', str(self.name))

    def get_commands(self):
        # return self.preparation
        to_execute = []
        if self.preparation:
            pattern = r"{0}".format(urllib.unquote(self.preparation.get('pattern')))
            # ok, lets see what we can do
            # did you select search files in dir or lines in file?
            if self.preparation.get('filterFile'):
                filter_file = self.preparation.get('filterFile')
                write_file = self.preparation.get('writeFile')
                placeholder = self.preparation.get('placeholder')
                copy = self.preparation.get('copy')
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
                            for command in self.commands:
                                # replace placeholder with actual created file
                                to_execute.append(command.replace('$file', new_file).replace('$line', new_file))

                            # look in side the new file for the placeholder and replace it
                            with codecs.open(new_file, 'rw+', encoding='utf8') as fw:
                                text = fw.read()
                                fw.seek(0)
                                fw.write(text.replace(placeholder, str(line)))
                                fw.close()

                else:
                    raise Exception('File does not exist!')

            elif self.preparation.get('searchDirectory'):
                search_directory = self.preparation.get('searchDirectory')
                if os.path.exists(search_directory):
                    # look for files matching the regex in a dir
                    all_matching_files = [name for name in glob.glob(os.path.join(search_directory, pattern))]

                    for match_file in all_matching_files:
                        # replace placeholder with matching file

                        for command in self.commands:
                            to_execute.append(command.replace('$file', match_file))
                else:
                    raise Exception('Directory does not exist!')
            else:
                raise Exception('Oops this shouldn\'t happen!')
        else:
            to_execute = self.commands

        return to_execute

    """
        Pop Guidance Tasks

        :return tasks
    """

    def pop_guidance(self):
        temp = self.guidance
        self.guidance = []
        return temp
