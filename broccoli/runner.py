import shlex
import subprocess


class Runner:

    def __init__(self):
        pass

    def run(self, arg):
        """
        TODO
        """
        args = shlex.split(arg)
        command = \
            subprocess.Popen(args, stdin=None if input is None else subprocess.PIPE, stdout=subprocess.PIPE, stderr=None)
        (stdout, stderr) = command.communicate(input)
        return (stdout, stderr), command
