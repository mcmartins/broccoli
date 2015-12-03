"""
    broccoli.Runner
    ~~~~~~~~~~~~~

    Manages the low level subprocess creation.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import os
import logging
import signal
import multiprocessing
import subprocess
from manager import Manager
import worker
import atexit


class Runner:

    def __init__(self, job):
        # change working directory
        os.chdir(job.wd)
        # ensure timeout
        signal.signal(signal.SIGALRM, self.__timeout)
        signal.alarm(job.timeout)
        # ensure nothing stays running if the tool blows for some reason
        atexit.register(self.cleanup)
        self.job = job
        self.manager = Manager(self.job)
        atexit.register(self.cleanup)
        self.pool = multiprocessing.Pool(multiprocessing.cpu_count())
        self.tasks_queue = multiprocessing.Queue()
        logging.info('Runner - Running Tasks for Job: %s.', str(job.name))
        logging.debug('Runner - Working Directory is: %s.', str(job.wd))
        logging.debug('Runner - Will Timeout after: %s seconds.', str(job.timeout))
        self.tasks_queue.put(job.get_tasks())
        self.__run()

    def __run(self):
        import time
        start_time = time.time()
        while True:
            try:
                tasks = self.tasks_queue.get()
                for task in tasks:
                    worker.do(task, self.tasks_queue)
                # logging.info('Runner - Starting processing Task: %s.', str(task.name))
                # sub_tasks = task.get_sub_tasks()
                # for sub_task in sub_tasks:
                #    worker.do(sub_task, self.manager)
                #    self.pool.apply_async(worker.do, args=(sub_task, self.manager,))
                logging.debug("--- %s seconds ---" % (time.time() - start_time))
            except IndexError:
                pass

    def __timeout(self, signum, frame):
        logging.info('Runner - Processing timed out after %s seconds.', str(self.job.timeout))
        exit(5)

    def cleanup(self):
        # ensure we kill all processes still running
        #self.manager.cleanup()
        #self.pool.close()
        logging.info('Runner - Bye Bye.')

    @staticmethod
    def do(sub_task, monitor):
        logging.info('Worker - Started SubTask: %s.', str(sub_task.id))
        tasks_to_monitor = []
        for command in sub_task.get_commands():
            p = subprocess.Popen(command, cwd=sub_task.get_parent().wd, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=True, preexec_fn=os.setsid)
            logging.debug('Worker - Process with pid %s is running command %s.', str(p.pid), str(command))
            tasks_to_monitor.append((sub_task, p))
        monitor.start(tasks_to_monitor)
        logging.info('Worker - We\'re done with SubTask %s. Launched %i command(s).', str(sub_task.id),
                     len(tasks_to_monitor))