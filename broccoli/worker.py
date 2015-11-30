import multiprocessing
import Queue
import logging
import subprocess
import os
from monitor import Monitor


class Worker(multiprocessing.Process):
    def __init__(self, job, queue, runner):
        super(Worker, self).__init__()
        self.job = job
        self.work_queue = queue
        self.runner = runner
        self.kill_received = False

    def run(self):
        logging.info(self.name + ' Started...')
        while True:
            processes = self.work_queue.get()
            if processes:
                tasks_to_monitor = []
                for process in processes:
                    for command in process.get_commands():
                        logging.debug('Worker - Running command: %s', str(command))
                        p = subprocess.Popen(command, cwd=self.job.wd, stdin=subprocess.PIPE,
                                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                   shell=True, preexec_fn=os.setsid)
                        self.runner.running_processes.append(p)
                        tasks_to_monitor.append((process.get_task(), p))
                        logging.debug('Worker - Task process pid is: %s', str(p.pid))

                    monitor = Monitor(self.runner, self)
                    monitor.start(tasks_to_monitor)
