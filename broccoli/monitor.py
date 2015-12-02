"""
    broccoli.Monitor
    ~~~~~~~~~~~~~

    Monitors running tasks.
    Manages all the lifecycle of the Job.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import util
import logging


class Monitor:
    def __init__(self, manager):
        self.id = util.short_unique_id()
        self.manager = manager
        self.sub_tasks = []
        self.waiting_tasks = []
        self.failed_tasks = []
        self.succeed_tasks = []
        self.exit = False

    def start(self, tasks):
        self.sub_tasks.extend(tasks)
        [self.manager.add_process(process.pid) for (sub_task, process) in tasks]
        logging.info('Monitor - Starting monitor ID: %s', str(self.id))
        logging.debug(
            'Monitor - Monitoring the following task(s): %s',
            ', '.join([sub_task.get_parent().name for (sub_task, process) in tasks]))
        # start monitor loop
        self.__monitor()

    def __monitor(self):
        while True:
            if self.exit:
                logging.info('Monitor - exit %s', str(self.exit))
                logging.info('Monitor - i dont get in here')
                break
            if self.sub_tasks:
                for (sub_task, process) in self.sub_tasks:
                    return_code = process.poll()
                    if return_code is not None:
                        # process finished
                        self.sub_tasks.remove((sub_task, process))
                        self.manager.remove_process(process.pid)
                        (std_out, std_err) = process.communicate()
                        if return_code == 0:
                            # sub_task finished successfully
                            logging.info('Monitor - FINISHED - Task %s, SubTask %s.', str(sub_task.get_parent().name),
                                         str(sub_task.id))
                            Monitor.__print_output(std_err, std_out)
                            if sub_task.get_parent().wait:
                                # should we wait for others to finish?
                                logging.info('Monitor - Waiting for other Tasks to finish.')
                                self.waiting_tasks.append((sub_task, process))
                                continue
                            else:
                                # good to go
                                self.succeed_tasks.append((sub_task, process))
                                if sub_task.get_parent().has_children():
                                    logging.info('Monitor - No need to wait for other processes to finish.')
                                    for (s, p) in self.sub_tasks:
                                        self.manager.kill_process(p.pid)
                                    logging.info('Monitor - Task has Children. Sending Tasks to Runner.')
                                    self.manager.add_tasks(sub_task.get_parent().get_children())
                                    self.exit = True
                                    logging.info('Monitor - exit %s', str(self.exit))
                                    break
                                else:
                                    self.__print_task_tree(sub_task.get_parent())
                                    logging.info('Monitor - Job Finished with success.')
                                    exit(0)

                        else:
                            # failed tasks goes here
                            logging.info('Monitor - FINISHED - Task Failure: %s', str(sub_task.get_parent().name))
                            Monitor.__print_output(std_err, std_out)
                            self.failed_tasks.append((sub_task, process))
                            if sub_task.get_parent().wait:
                                # hum this task failed and it seems to be waiting for
                                # the output of another at the same level, the most probable scenario
                                # is that it won't work from here on. Better to kill the Job now.
                                logging.info('Monitor - Job Finished with errors.')
                                exit(1)
                            else:
                                # hum we cannot proceed to the children tasks because this one failed
                                # lets see if the Job has still tasks running
                                if self.manager.has_running_processes():
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
                    for (sub_task, process) in self.waiting_tasks:
                        if sub_task.get_parent().has_children():
                            self.manager.add_tasks(sub_task.get_parent().get_children())
                # this branch is over no need to monitor anymore
                # a new monitor is created for each branch of tasks
                break
        logging.info('Monitor - Finishing Monitor ID: %s', str(self.id))

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
        while task.get_parent() is not None:
            task = task.get_parent()
            tasks.append(task.name)
        logging.info('Monitor - The Job finished with the following order:')
        for i, task in enumerate(reversed(tasks)):
            logging.info('\t%s: %s', ordinal(i + 1), task)
