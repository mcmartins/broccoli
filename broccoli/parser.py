import json
import sys
import os.path
import logging
import jsonschema
import pkg_resources
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


class InvalidInput(jsonschema.exceptions.ValidationError):


    """
    Raised when the input provided is not valid against the schema.

    Attributes:
        message  -- explanation of the attribute(s) that is(are) invalid
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def parse(arg):
    if os.path.isfile(arg):
        config = json.loads(open(arg).read().decode("utf-8"))
    else:
        config = json.load(arg)
    # validate the input, will throw an exception if fails
    __validate(config)
    # TODO Sanitize all input values
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


def __validate(input_data):
    resource_package = __name__
    resource_path = os.path.join('..', 'schema', 'broccoli_schema.json')
    resource = pkg_resources.resource_string(resource_package, resource_path)
    schema = json.loads(resource)
    try:
        jsonschema.validate(input_data, schema)
    except jsonschema.exceptions.ValidationError, e:
        message = 'Invalid input provided. Message is: ' + e.message
        raise InvalidInput(message)
