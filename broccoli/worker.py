"""
    broccoli.Worker
    ~~~~~~~~~~~~~

    A Worker is responsible for process sub_tasks

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import multiprocessing
import logging
import util
from monitor import Monitor


class Worker(multiprocessing.Process):
    def __init__(self, job, queue, runner):
        super(Worker, self).__init__()
        self.id = util.short_unique_id()
        self.__job = job
        self.__work_queue = queue
        self.__runner = runner
        self.__alive = True
    
    """
        Overrides Process.run()
    """
    
    def run(self):
        logging.info('Worker - %s with id %s started...', str(self.name), str(self.id))
        while self.__alive:
            sub_task = self.__work_queue.get()
            if sub_task is None:
                break
            monitor = Monitor(self.__runner)
            sub_task.process(monitor)
        logging.info('Worker - %s with id %s killed...', str(self.name), str(self.id))


    """
        Kill the worker
    """

    def kill(self):
        self.__work_queue.put(None)
