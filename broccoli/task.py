import uuid
import logging
import multiprocessing
import re
import fileinput
import shutil
import glob
import string

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


class Task:
    """
       Task constructor

       :param name
       :param command
    """

    def __init__(self, taskConfig):
        self.id = uuid.uuid4()
        self.name = taskConfig.get('taskName')
        self.description = taskConfig.get('taskDescription')
        self.wait = taskConfig.get('wait')
        self.run = taskConfig.get('run')
        self.guidance = multiprocessing.Queue()
        for guidanceConfig in taskConfig.get('guidance'):
            self.guidance.put(Task(guidanceConfig))
        logging.debug('New Task created: %s', str(self.name))

    def get_commands(self):
        to_execute = []
        # look matching regex in each line of a file
        all_lines = [re.findall(r'f\(\s*([^,]+)\s*,\s*([^,]+)\s*\)', line) for line in open('fileToRead')]
        for line in all_lines:
            # create a copy of the file with the same name plus
            new_filename = self.__format_filename(line+'fileToWrite')
            shutil.copy2('fileToWrite', new_filename)
            
            # get commands to execute
            commands = []
            for command in commands:
                # replace placeholder with actual created file
                to_execute.append(command.replace('$file', new_filename))
            
            # look in side the new file for the placeholder and replace it
            for l in fileinput.input(new_filename, inplace=True):
                print(line.replace('placeholder', l), '')

        # look for files matching the regex in a dir
        all_files = [name for name in glob.glob('dir/*[0-9].*')]
        for file in all_files:
            commands = []
            for command in commands:
                # replace placeholder with matching file
                to_execute.append(command.replace('$file', file))
        
        return to_execute
        
    def __format_filename(self, s):
        """
        Take a string and return a valid filename constructed from the string.
        Uses a whitelist approach: any characters not present in valid_chars are
        removed. Also spaces are replaced with underscores.
         
        Note: this method may produce invalid filenames such as ``, `.` or `..`
        When I use this method I prepend a date string like '2009_01_15_19_46_32_'
        and append a file extension like '.txt', so I avoid the potential of using
        an invalid filename.
        """
        valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in s if c in valid_chars)
        filename = filename.replace(' ','_') # I don't like spaces in filenames.
        return filename

    """
        Pop Guidance Tasks

        :return tasks
    """

    def pop_guidance(self):
        temp = self.guidance
        self.guidance = []
        return temp
