import uuid

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

    def __init__(self, name='Anonymous', description='', wait=False, command=''):
        self.id = uuid.uuid4()
        self.parent = None
        self.name = name
        self.description = description
        self.wait = wait
        self.command = command
        self.guidance = []

    def __init__(self, config):
        self.id = uuid.uuid4()
        self.name = config.get('taskName')
        self.description = config.get('taskDescription')
        self.wait = config.get('wait')
        self.run = config.get('run')
        self.guidance = []
        for guidanceConfig in config.get('guidance'):
            self.guidance.append(Task(guidanceConfig))

    def get_commands(self):
        commands = []
        import re
        all_lines = [re.findall(r'f\(\s*([^,]+)\s*,\s*([^,]+)\s*\)', line) for line in open('fileToRead')]

        import fileinput
        for line in all_lines:
            import shutil
            shutil.copy2('fileToWrite', 'fileToWrite'+line)

            for l in fileinput.input('fileToWrite'+line, inplace=True):
                print(line.replace('placeholder', l), '')

        return commands

    """
        Pop Guidance Tasks

        :return tasks
    """

    def pop_guidance(self):
        temp = self.guidance
        self.guidance = []
        return temp
