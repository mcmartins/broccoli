import multiprocessing
import commands


class Worker(multiprocessing.Process):
    def __init__(self, work_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.kill_received = False

    def run(self):
        while (not self.kill_received) and (not self.work_queue.empty()):
            try:
                task = self.work_queue.get_nowait()
            except Exception:
                break

            for command in task.get_commands:
                ret = self.__start_sub_process(command)
                self.result_queue.put(ret)

    def __start_sub_process(self, command):
        try:
            # invoke runner
            return commands.getoutput(command)
        except Exception:
            return "Error executing command %s" % command

def run(job, num_processes=4):
    work_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    tasks = job.pop_tasks()
    for task in tasks:
        work_queue.put(task)

    workers = []
    for i in range(num_processes):
        workers.append(Worker(work_queue, result_queue))
        workers[i].start()

