"""
    broccoli.Manager
    ~~~~~~~~~~~~~

    Manages the low level subprocess creation.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import os
import util
import signal
import logging
import multiprocessing


def monitor(thread_util, sub_tasks):
    unique_id = util.short_unique_id()
    exit_event = multiprocessing.Event()
    waiting_tasks = []
    logging.info('Manager - Starting Manager ID: %s', str(unique_id))
    while not exit_event.is_set():
        non_finished_tasks = []
        if sub_tasks:
            for (sub_task, process) in sub_tasks:
                return_code = process.poll()
                if return_code is not None:
                    # process finished
                    thread_util[1].remove(process.pid)
                    (std_out, std_err) = process.communicate()
                    if return_code == 0:
                        # sub_task finished successfully
                        logging.info('Manager - FINISHED - Task %s, SubTask %s.', str(sub_task.get_parent().name),
                                     str(sub_task.id))
                        __print_output(std_err, std_out)
                        if sub_task.get_parent().wait:
                            # should we wait for others to finish?
                            logging.info('Manager - Waiting for other Tasks to finish.')
                            waiting_tasks.append((sub_task, process))
                            continue
                        else:
                            # good to go
                            if sub_task.get_parent().has_children():
                                logging.info('Manager - No need to wait for other processes to finish.')
                                for (s, p) in sub_tasks:
                                    __kill_process(p.pid)
                                logging.info('Manager - Task has Children. Sending Tasks to Processing Queue.')
                                for task in sub_task.get_parent().get_children():
                                    thread_util[0].put(task)
                                exit_event.set()
                                return
                            else:
                                __print_task_tree(sub_task.get_parent())
                                logging.info('Manager - Job Finished with success.')
                                exit_event.set()
                                thread_util[2].set()
                                exit(0)

                    else:
                        # failed tasks goes here
                        logging.info('Manager - FINISHED - Task Failure: %s', str(sub_task.get_parent().name))
                        __print_output(std_err, std_out)
                        if sub_task.get_parent().wait:
                            # hum this task failed and it seems to be waiting for
                            # the output of another at the same level, the most probable scenario
                            # is that it won't work from here on. Better to kill the Job now.
                            logging.info('Manager - Job Finished with errors.')
                            exit_event.set()
                            thread_util[2].set()
                            exit(1)
                        else:
                            # hum we cannot proceed to the children tasks because this one failed
                            # lets see if the Job has still tasks running
                            if False:
                                # OK fine, there are still other tasks at the same level running
                                continue
                            else:
                                # seems we were waiting for this one to complete
                                # better to kill this now
                                logging.info('Manager - Job Finished with errors.')
                                exit_event.set()
                                thread_util[2].set()
                                exit(2)

                else:
                    non_finished_tasks.append((sub_task, process))
        else:
            # are there tasks waiting for others to finish?
            if waiting_tasks:
                for (sub_task, process) in waiting_tasks:
                    if sub_task.get_parent().has_children():
                        logging.info('Manager - Task has Children. Sending Tasks to self.manager.')
                        thread_util[0].put.put(sub_task.get_parent().get_children())
                        exit_event.set()
                        break
                    else:
                        __print_task_tree(sub_task.get_parent())
                        logging.info('Manager - Job Finished with success.')
                        exit_event.set()
                        thread_util[2].set()
                        exit(0)
        # remove elements that were already processed
        sub_tasks = non_finished_tasks

    logging.info('Manager - Finishing Manager ID: %s', str(unique_id))


def __kill_process(process):
    logging.info('Manager - Killing process %s', str(process))
    try:
        os.kill(process, signal.SIGTERM)
    except OSError:
        logging.info('Manager - Process with pid %s is not present. Skipping...', str(process))


def __print_output(std_err, std_out):
    if std_err:
        logging.debug('Manager - Standard error (stderr):\n%s', str(std_err))
    if std_out:
        logging.debug('Manager - Standard output (stdout):\n%s', str(std_out))


def __print_task_tree(task):
    def ordinal(n):
        return '%d%s' % (n, 'tsnrhtdd'[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10::4])

    tasks = [task.name]
    while task.get_parent() is not None:
        task = task.get_parent()
        tasks.append(task.name)
    logging.info('Manager - The Job finished with the following order:')
    for i, task in enumerate(reversed(tasks)):
        logging.info('\t%s: %s', ordinal(i + 1), task)
