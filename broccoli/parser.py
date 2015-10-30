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


class InvalidInput(AttributeError):
    """
    Raised when the input provided is not a file or valid JSON string

    Attributes:
        message  --
    """

    def __init__(self, message):
        self.message = 'Invalid input provided. ' + message

    def __str__(self):
        return repr(self.message)


class MalformedJSONInput(jsonschema.exceptions.ValidationError):
    """
    Raised when the input provided is not valid against the schema.

    Attributes:
        message  -- explanation of the attribute(s) that is(are) invalid
    """

    def __init__(self, message):
        self.message = 'Invalid input provided. ' + message

    def __str__(self):
        return repr(self.message)


def parse(arg):
    if os.path.isfile(arg):
        config = json.loads(open(arg).read().decode("utf-8"))
    else:
        try:
            config = json.load(arg)
        except AttributeError:
            raise InvalidInput('Input provided is not an existing file or valid JSON string!')
    # validate the input, will throw an exception if fails
    __validate(config)
    logging.info('Parsing input...')
    logging.debug('Input is: ' + str(config))
    broccoli_job = Job(config.get('jobName'), config.get('workingDir'), config.get('timeout'))
    for task in config.get('tasks'):
        broccoli_job.add_task(
            __build_task(Task(task.get('taskName'), task.get('command'), task.get('wait')), task.get('guidance')))
    logging.info('New Job created: ' + str(broccoli_job.name))
    return broccoli_job


def __build_task(parent, guidance):
    if guidance:
        for guidanceTask in guidance:
            task = Task(guidanceTask.get('taskName'), guidanceTask.get('command'), guidanceTask.get('wait'))
            parent.add_guidance(task)
            return __build_task(parent, guidanceTask.get('guidance'))
    return parent


def __validate(input_data):
    schema_path = os.path.join('schema', 'broccoli_schema.json')
    schema = pkg_resources.resource_string(__name__, schema_path)
    try:
        jsonschema.validate(input_data, json.loads(schema))
    except jsonschema.exceptions.ValidationError, e:
        raise MalformedJSONInput(e.message)
