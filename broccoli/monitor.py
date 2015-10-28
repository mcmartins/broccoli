import logging

"""
    broccoli.Monitor
    ~~~~~~~~~~~~~

    Monitors running tasks.
    Manages all the lifecycle of the Job.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


class Monitor:
    # these is a static private variable shared among all instances of the monitor
    # this way we can keep track of everything that is running
    # this is useful to kill running processes when we reach a solution
    __running_processes = []

    def __init__(self, runner):
        self.runner = runner
        # tasks management variables
        self.tasks = []
        self.waiting_tasks = []
        self.failed_tasks = []
        self.succeed_tasks = []

    def start(self, tasks):
        self.tasks.append(tasks)
        self.__running_processes.append(process for (task, process) in tasks)
        logging.info('Starting monitoring the following tasks: ' + tasks)
        # start monitor loop
        self.__monitor()

    def __monitor(self):
        while True:
            if self.tasks:
                for (task, process) in self.tasks:
                    return_code = process.poll()
                    if return_code is not None:
                        # process finished
                        self.tasks.remove((task, process))
                        self.__running_processes.remove(process)
                        if return_code >= 0:
                            # task finished successfully
                            if task.wait:
                                # should we wait for others to finish?
                                self.waiting_tasks.append((task, process))
                                continue
                            else:
                                # good to go
                                self.succeed_tasks.append((task, process))
                                if task.get_guidance:
                                    self.runner.add_tasks(task.get_guidance())
                                else:
                                    self.__exit_gracefully()
                        else:
                            # failed tasks goes here
                            self.failed_tasks.append((task, process))
                            if task.wait:
                                # hmmm this task seems to be waiting for the output of another at the same level
                                # the most probable scenario is that it won't work from here on
                                # better to kill this now
                                self.__exit_gracefully()
                            else:
                                # hmmm we cannot proceed to the guidance tasks because this one failed
                                # lets see if we can still proceed
                                if self.tasks:
                                    # OK fine, there are still other tasks at the same level running
                                    continue
                                else:
                                    # seems we were waiting for this one to complete
                                    # better to kill this now
                                    self.__exit_gracefully()
            else:
                # are there tasks waiting for others to finish?
                if self.waiting_tasks:
                    for (task, process) in self.waiting_tasks:
                        if task.get_guidance:
                            self.runner.add_tasks(task.get_guidance())
                # this branch is over no need to monitor anymore
                # a new monitor is created for each branch of tasks
                break

    def __exit_gracefully(self):
        self.__kill_all()
        logging.info('Processing finished...')
        exit(0)

    def __kill_all(self):
        for process in self.__running_processes:
            logging.info('Killing running process: ' + process.id)
            process.kill()
