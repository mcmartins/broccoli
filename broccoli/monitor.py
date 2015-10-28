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

    def __init__(self, runner):
        self.runner = runner
        # tasks management variables
        self.tasks = []
        self.waiting_tasks = []
        self.failed_tasks = []
        self.succeed_tasks = []

    def start(self, tasks):
        self.tasks.append(tasks)
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
                        self.runner.__running_processes.remove(process)
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
                                    self.runner.__exit_gracefully()
                        else:
                            # failed tasks goes here
                            self.failed_tasks.append((task, process))
                            if task.wait:
                                # hmmm this task seems to be waiting for the output of another at the same level
                                # the most probable scenario is that it won't work from here on
                                # better to kill this now
                                self.runner.__exit_gracefully()
                            else:
                                # hmmm we cannot proceed to the guidance tasks because this one failed
                                # lets see if we can still proceed
                                if self.tasks:
                                    # OK fine, there are still other tasks at the same level running
                                    continue
                                else:
                                    # seems we were waiting for this one to complete
                                    # better to kill this now
                                    self.runner.__exit_gracefully()
            else:
                # are there tasks waiting for others to finish?
                if self.waiting_tasks:
                    for (task, process) in self.waiting_tasks:
                        if task.get_guidance:
                            self.runner.add_tasks(task.get_guidance())
                # this branch is over no need to monitor anymore
                # a new monitor is created for each branch of tasks
                break
