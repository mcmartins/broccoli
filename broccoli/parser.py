import json
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
    logging.info('Parsing input...')
    logging.debug('Input is: ' + str(config))
    broccoli_job = Job(config.get('jobName'), config.get('workingDir'), config.get('timeout'))
    for task in config.get('tasks'):
        broccoli_job_task = __resolve_guidance(Task(task.get('taskName'), task.get('command')), task.get('guidance'))
        broccoli_job.add_task(broccoli_job_task)
    logging.info('New Job created: ' + str(broccoli_job.name))
    return broccoli_job


def __resolve_guidance(parent, guidance):
    if guidance:
        for guidanceTask in guidance:
            task = Task(guidanceTask.get('taskName'), guidanceTask.get('command'), guidanceTask.get('wait'))
            parent.add_guidance(task)
            return __resolve_guidance(task, guidanceTask.get('guidance'))
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
