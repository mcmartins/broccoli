import uuid
import logging
import multiprocessing
import re
import codecs
import shutil
import glob
import string
import os
import urllib


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
    @staticmethod
    def generate_unique_id():
        return str(uuid.uuid4())

    """
       Task constructor

       :param name
       :param command
    """

    def __init__(self, task_config):
        self.id = uuid.uuid4()
        self.name = task_config.get('taskName')
        self.description = task_config.get('taskDescription')
        self.wait = task_config.get('wait')
        self.execute = task_config.get('execute')
        self.guidance = []  # multiprocessing.Queue()
        guidance_config = task_config.get('guidance')
        if guidance_config:
            for config in guidance_config:
                self.guidance.append(Task(config))
        logging.debug('New Task created: %s', str(self.name))

    def get_commands(self):
        to_execute = []
        commands = [command for command in self.execute.get('commands')]
        for_each = self.execute.get('forEach')
        if for_each:
            matching_regex = r"{0}".format(urllib.unquote(for_each.get('matching'))) # ^given.*?:\s*\d+([^.\#]*)[\#[^.]*]?\.\s*\[.*?\]\.
            read = for_each.get('in')
            if read:
                if os.path.isfile(read):
                    # look matching regex in each line of a file
                    do = for_each.get('do')
                    write = do.get('write')
                    replace = do.get('replace')
                    with open(read, "r") as f:
                        all_matching_lines = re.findall(matching_regex, f.read(), re.MULTILINE)
                        f.close()

                    # create a copy of the file with the same name plus
                    for line in filter(None, all_matching_lines):
                        new_filename = self.__format_filename(self.generate_unique_id() + write)
                        shutil.copy2(write, new_filename)

                        # get commands to execute
                        for command in commands:
                            # replace placeholder with actual created file
                            to_execute.append(command.replace('$file', new_filename).replace('$line', new_filename))

                        # look in side the new file for the placeholder and replace it
                        with codecs.open(new_filename, 'rw+', encoding='utf8') as f:
                            text = f.read()
                            f.seek(0)
                            f.write(text.replace(replace, str(line)))
                            f.close()
                        break

                elif os.path.isdir(read):
                    # look for files matching the regex in a dir
                    all_matching_files = [name for name in glob.glob(os.path.join(read, matching_regex))]
                    for f in all_matching_files:
                        # replace placeholder with matching file
                        for command in commands:
                            to_execute.append(command.replace('$file', f))
            else:
                to_execute = commands
        return to_execute

    @staticmethod
    def __format_filename(s):
        """
        Take a string and return a valid filename constructed from the string.
        Uses a whitelist approach: any characters not present in valid_chars are
        removed. Also spaces are replaced with underscores.
         
        Note: this method may produce invalid filenames such as ``, `.` or `..`
        When I use this method I prepend a date string like '2009_01_15_19_46_32_'
        and append a file extension like '.txt', so I avoid the potential of using
        an invalid filename.
        """
        valid_chars = "_.() %s%s" % (string.ascii_letters, string.digits)
        filename = ''.join(c for c in s if c in valid_chars)
        filename = filename.replace(' ', '_')  # I don't like spaces in filenames.
        filename = os.path.splitext(filename)[0]
        return filename

    """
        Pop Guidance Tasks

        :return tasks
    """

    def pop_guidance(self):
        temp = self.guidance
        self.guidance = []
        return temp
