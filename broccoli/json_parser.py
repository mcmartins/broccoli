"""
    broccoli.parser
    ~~~~~~~~~~~~~

    This is a JSON parser.
    It reads a file or string and returns the dictionary of attributes.

    See 'broccoli_schema.json' for details on usage.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import json
import os.path
import logging
import jsonschema
import pkg_resources


class InvalidInput(AttributeError):
    """
    Raised when the input provided is not a file or valid JSON string

    Attributes:
        message  --
    """

    def __init__(self, message):
        self.message = 'Invalid input provided. Should be in JSON format and should be a File or String. ' + message

    def __str__(self):
        return repr(self.message)


class MalformedJSONInput(jsonschema.exceptions.ValidationError):
    """
    Raised when the input provided is not valid against the schema.

    Attributes:
        message  -- explanation of the attribute(s) that is(are) invalid
    """

    def __init__(self, message):
        self.message = 'The JSON input is invalid. ' + message

    def __str__(self):
        return repr(self.message)


def parse(arg):
    if os.path.isfile(arg):
        config = json.loads(open(arg).read().decode("utf-8"))
    else:
        try:
            config = json.JSONEncoder().encode(json.loads(json.dumps(arg)))
        except AttributeError:
            raise InvalidInput('Input provided is not an existing file or valid JSON string!')
    # validate the input and raise an exception if fails
    __validate(config)
    logging.info('JSON Parser - Parsing input...')
    logging.debug('JSON Parser - Input is: %s', str(config))
    return config


def __validate(input_data):
    schema_path = os.path.join('schema', 'broccoli_schema.json')
    schema = pkg_resources.resource_string(__name__, schema_path)
    try:
        jsonschema.validate(input_data, json.loads(schema))
    except jsonschema.exceptions.ValidationError, e:
        raise MalformedJSONInput(e.message)
