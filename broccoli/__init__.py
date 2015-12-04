#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging

"""
    broccoli.__init___
    ~~~~~~~~~~~~~

    Initialize module with default logging config.

    :copyright: 2015 Manuel Martins, see AUTHORS for more details
    :license: Apache 2.0, see LICENSE for more details
"""

import copy_reg
import types

__version__ = '0.0.2'

logging.basicConfig(format='%(asctime)s - [%(levelname)s] - %(message)s', level=logging.INFO)


def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    if func_name.startswith('__') and not func_name.endswith('__'):  # deal with mangled names
        cls_name = cls.__name__.lstrip('_')
        func_name = '_' + cls_name + func_name
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.__mro__:
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)


copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)
