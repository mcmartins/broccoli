"""
    broccoli.Manager
    ~~~~~~~~~~~~~

    The Manager monitors the Sub Tasks and signal the Job on completion or guidance.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import util
import logging
import multiprocessing


def monitor(thread_util, sub_tasks):
    unique_id = util.short_unique_id()
    exit_event = multiprocessing.Event()
    waiting_tasks = []
    logging.debug('Manager - Starting ID [%s].', str(unique_id))
    while not exit_event.is_set() or not thread_util.is_kill_event_set():
        non_finished_tasks = []
        if sub_tasks:
            for (sub_task, process) in sub_tasks:
                return_code = process.poll()
                if return_code is not None:
                    # process finished
                    thread_util.remove_process(sub_task.get_parent().id, process.pid)
                    (std_out, std_err) = process.communicate()
                    if return_code == 0:
                        # sub_task finished successfully
                        logging.info('Manager - FINISHED - Task [%s], SubTask [%s].', str(sub_task.get_parent().name),
                                     str(sub_task.id))
                        util.print_output(std_err, std_out)
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
                                    util.kill_process(p.pid)
                                    thread_util.remove_process(s.get_parent().id, p.pid)
                                logging.info('Manager - Task has Children. Sending Tasks to Processing Queue.')
                                for task in sub_task.get_parent().get_children():
                                    thread_util.add_task(task)
                                exit_event.set()
                                break
                            else:
                                util.print_task_tree(sub_task.get_parent())
                                logging.info('Manager - Job Finished with success.')
                                exit_event.set()
                                thread_util.kill(0)
                                exit(0)
                    else:
                        # failed tasks goes here
                        logging.info('Manager - FINISHED - Task Failure [%s], SubTask [%s].',
                                     str(sub_task.get_parent().name), str(sub_task.id))
                        util.print_output(std_err, std_out)
                        if sub_task.get_parent().fail_tolerant:
                            logging.info('Manager - The Task is Fail Tolerant.')
                            if thread_util.has_running_processes(sub_task.get_parent().id):
                                # should we wait for others to finish?
                                logging.info('Manager - Waiting for other Tasks to finish.')
                                continue
                            else:
                                # good to go
                                if sub_task.get_parent().has_children():
                                    logging.info('Manager - No need to wait for other processes to finish.')
                                    for (s, p) in sub_tasks:
                                        util.kill_process(p.pid)
                                        thread_util.remove_process(s.get_parent().id, p.pid)
                                    logging.info('Manager - Task has Children. Sending Tasks to Processing Queue.')
                                    for task in sub_task.get_parent().get_children():
                                        thread_util.add_task(task)
                                    exit_event.set()
                                else:
                                    util.print_task_tree(sub_task.get_parent())
                                    logging.info(
                                        "Manager - Job Finished with success, but Fail Tolerance has been applied.")
                                    exit_event.set()
                                    thread_util.kill(0)
                                    exit(0)
                        elif sub_task.get_parent().wait:
                            # hum this task failed and it seems to be waiting for
                            # the output of another at the same level, the most probable scenario
                            # is that it won't work from here on. Better to kill the Job now.
                            logging.info('Manager - Job Finished with errors.')
                            exit_event.set()
                            thread_util.kill(1)
                            exit(1)
                        else:
                            # hum we cannot proceed to the children tasks because this one failed
                            # lets see if the Job has still tasks running
                            if thread_util.has_running_processes(sub_task.get_parent().id):
                                # OK fine, there are still other tasks at the same level running
                                continue
                            else:
                                # seems we were waiting for this one to complete
                                # better to kill this now
                                logging.info('Manager - Job Finished with errors.')
                                exit_event.set()
                                thread_util.kill(2)
                                exit(2)
                else:
                    non_finished_tasks.append((sub_task, process))
        else:
            # are there tasks waiting for others to finish?
            if waiting_tasks:
                for (sub_task, process) in waiting_tasks:
                    if sub_task.get_parent().has_children():
                        logging.info('Manager - Task has Children. Sending Tasks to self.manager.')
                        thread_util.add_task(sub_task.get_parent().get_children())
                        exit_event.set()
                        break
                    else:
                        util.print_task_tree(sub_task.get_parent())
                        logging.info('Manager - Job Finished with success.')
                        exit_event.set()
                        thread_util.kill(0)
                        exit(0)
            else:
                exit_event.set()
                break
        # remove elements that were already processed
        sub_tasks = non_finished_tasks

    logging.debug('Manager - Finished ID [%s].', str(unique_id))
    return
