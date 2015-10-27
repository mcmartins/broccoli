import json
from broccoli.job import Job
from broccoli.task import Task


class Builder:

    def __init__(self, arg):
        """
        TODO should check if it is a file or a string as input
        """
        self.config = json.loads(open(arg).read())

    def build(self):
        job = Job(self.config.jobName, self.config.workingDir, self.config.timeout)
        for t in self.config.tasks:
            task = Task(t.taskName, t.command)
            self.__resolve_guidance(task, t.guidance)
            for g in t.guidance:
                guidance = Task(g.taskName, g.command)
                task.add_guidance(guidance)
            job.add_task(task)
        return job

    def __resolve_guidance(self, parent, task):
        for g in task.guidance:
            guidance = Task(g.taskName, g.command)
            parent.add_guidance(guidance)
            return self.__resolve_guidance(g)
        return task