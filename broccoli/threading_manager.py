"""
    broccoli.Threading
    ~~~~~~~~~~~~~



    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

from multiprocessing.managers import BaseManager
from multiprocessing.managers import BaseListProxy
from multiprocessing.managers import DictProxy
from multiprocessing.managers import BaseProxy
from multiprocessing.managers import EventProxy
from multiprocessing.managers import PoolProxy
from multiprocessing import Event
from multiprocessing import Pool
from Queue import Queue
import util


class ThreadingManager(BaseManager):
    pass


class SetProxy(BaseProxy):
    def put(self, item, block=True, timeout=None):
        return self._callmethod('put', [item, block, timeout])

    def get_nowait(self):
        return self._callmethod('get_nowait')


class SetQueue(Queue):
    def __init__(self):
        Queue.__init__(self)
        self.all_items = list()

    def put(self, item, block=True, timeout=None):
        if item not in self.all_items:
            self.all_items.append(item)
            Queue.put(self, item, block, timeout)

    def get_nowait(self):
        # item = Queue.get_nowait(self)
        # self.all_items.remove(item)
        return Queue.get_nowait(self)


class ThreadingPropertiesProxy(BaseProxy):
    def add_task(self, item):
        return self._callmethod('add_task', [item])

    def get_task(self):
        return self._callmethod('get_task')

    def kill(self, code):
        return self._callmethod('kill', [code])

    def is_kill_event_set(self):
        return self._callmethod('is_kill_event_set')

    def get_result_code(self):
        return self._callmethod('get_result_code')

    def add_process(self, task_id, process_id):
        return self._callmethod('add_process', [task_id, process_id])

    def remove_process(self, task_id, process_id):
        return self._callmethod('remove_process', [task_id, process_id])

    def has_running_processes(self, task_id):
        return self._callmethod('has_running_processes', [task_id])


class ThreadingProperties(dict):
    def __init__(self, **kwargs):
        super(ThreadingProperties, self).__init__(**kwargs)
        self.multiprocessing_manager = ThreadingManager()
        self.multiprocessing_manager.start()
        self.tasks_queue = self.multiprocessing_manager.SetQueue()
        self.running_processes = self.multiprocessing_manager.List()
        self.kill_event = self.multiprocessing_manager.Event()
        self.result_code = 0
        self.has_sub_tasks_to_process = False

    def add_task(self, item):
        self.tasks_queue.put(item)

    def get_task(self):
        return self.tasks_queue.get_nowait()

    def kill(self, code=0):
        self.kill_event.set()
        self.result_code = code
        self.__kill_all_processes()

    def is_kill_event_set(self):
        self.kill_event.is_set()

    def get_result_code(self):
        return self.result_code

    def add_process(self, task_id, process_id):
        self.running_processes.append((task_id, process_id))

    def remove_process(self, task_id, process_id):
        if (task_id, process_id) in self.running_processes:
            self.running_processes.remove((task_id, process_id))

    def __kill_all_processes(self):
        if self.running_processes:
            for (task_id, process_id) in self.running_processes:
                util.kill_process(process_id)

    def has_running_processes(self, task_id):
        if self.running_processes:
            for (rtask_id, process_id) in self.running_processes:
                if rtask_id == task_id:
                    return True
        return False


ThreadingManager.register('SetQueue', SetQueue, proxytype=SetProxy)
ThreadingManager.register('List', list, proxytype=BaseListProxy)
ThreadingManager.register('Dict', dict, proxytype=DictProxy)
ThreadingManager.register('Event', Event, proxytype=EventProxy)
ThreadingManager.register('Pool', Pool, proxytype=PoolProxy)
ThreadingManager.register('ThreadingProperties', ThreadingProperties, proxytype=ThreadingPropertiesProxy)
