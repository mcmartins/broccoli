import uuid
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
        self.id = uuid.uuid4()
        self.runner = runner
        # tasks management variables
        self.tasks = []
        self.waiting_tasks = []
        self.failed_tasks = []
        self.succeed_tasks = []

    def start(self, tasks):
        self.tasks.extend(tasks)
        logging.info('Monitor - Starting monitor ID: %s', str(self.id))
        logging.debug(
            'Monitor - Monitoring the following task(s): %s', str([task.name for (task, process) in tasks]))
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
                        self.runner.running_processes.remove(process)
                        (std_out, std_err) = process.communicate()
                        if return_code == 0:
                            # task finished successfully
                            logging.info('Monitor - FINISHED - Task: %s', str(task.name))
                            Monitor.__print_output(std_err, std_out)
                            if task.wait:
                                # should we wait for others to finish?
                                logging.info('Monitor - Waiting for others Tasks to finish.')
                                self.waiting_tasks.append((task, process))
                                continue
                            else:
                                # good to go
                                self.succeed_tasks.append((task, process))
                                if task.guidance:
                                    logging.info('Monitor - Task has Guidance. Sending Sub Tasks to Runner.')
                                    self.runner.add_tasks(task.pop_guidance())
                                else:
                                    self.__print_task_tree(task)
                                    logging.info('Monitor - Job Finished with success.')
                                    exit(0)
                        else:
                            # failed tasks goes here
                            logging.info('Monitor - FINISHED - Task Failure: %s', str(task.name))
                            Monitor.__print_output(std_err, std_out)
                            self.failed_tasks.append((task, process))
                            if task.wait:
                                # hum this task failed and it seems to be waiting for
                                # the output of another at the same level, the most probable scenario
                                # is that it won't work from here on. Better to kill the Job now.
                                logging.info('Monitor - Job Finished with errors.')
                                exit(1)
                            else:
                                # hum we cannot proceed to the guidance tasks because this one failed
                                # lets see if the Job has still tasks running
                                if self.runner.running_processes:
                                    # OK fine, there are still other tasks at the same level running
                                    continue
                                else:
                                    # seems we were waiting for this one to complete
                                    # better to kill this now
                                    logging.info('Monitor - Job Finished with errors.')
                                    exit(2)
            else:
                # are there tasks waiting for others to finish?
                if self.waiting_tasks:
                    for (task, process) in self.waiting_tasks:
                        if task.guidance:
                            self.runner.add_tasks(task.pop_guidance())
                # this branch is over no need to monitor anymore
                # a new monitor is created for each branch of tasks
                break

    @staticmethod
    def __print_output(std_err, std_out):
        if std_err:
            logging.debug('Monitor - Standard error (stderr):\n%s', str(std_err))
        if std_out:
            logging.debug('Monitor - Standard output (stdout):\n%s', str(std_out))

    @staticmethod
    def __print_task_tree(task):
        def ordinal(n):
            return '%d%s' % (n, 'tsnrhtdd'[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

        tasks = [task.name]
        while task.parent is not None:
            task = task.parent
            tasks.append(task.name)
        logging.info('The Job finished with the following order:')
        for i, task in enumerate(reversed(tasks)):
            logging.info('%s: %s', ordinal(i + 1), task)

