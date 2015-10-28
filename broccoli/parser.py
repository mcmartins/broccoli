import json
import os.path
import logging
import pprint
from job import Job
from task import Task

"""
    broccoli.parser
    ~~~~~~~~~~~~~

    This is a JSON parser.
    It reads a file or string and converts into a Job object.

    See 'broccoli_schema.json' for details on usage.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""


def parse(arg):
    """
    TODO validate the input with the schema
    """
    if os.path.isfile(arg):
        config = json.loads(open(arg).read().decode("utf-8"))
    else:
        config = json.load(arg)
    """
    TODO Sanitize all input values
    """
    logging.info('Parsing input...')
    logging.debug(config)
    broccoli_job = Job(config['jobName'], config['workingDir'], config['timeout'])
    for task in config['tasks']:
        broccoli_job_task = Task(task['taskName'], task['command'])
        if 'guidance' in task.keys():
            broccoli_job_task = __resolve_guidance(broccoli_job_task, task['guidance'])
        broccoli_job.add_task(broccoli_job_task)
    logging.info('New Job created...')
    return broccoli_job


def __resolve_guidance(parent, guidance):
    for guidanceTask in guidance:
        task = Task(guidanceTask['taskName'], guidanceTask['command'], guidanceTask['wait'])
        parent.add_guidance(task)
        if 'guidance' in guidanceTask.keys():
            return __resolve_guidance(task, guidanceTask['guidance'])
    return parent

