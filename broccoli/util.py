import uuid
from time import time

"""
    Short unique id generated based on time
    e.g.: short_unique_id() = {str} '83c31574873f'
"""


def short_unique_id():
    return hex(int(time() * 999999))[2:]


"""
    UUID without '-'
    e.g.: unique_id() = {str} ''cb2423b336e44a2da9256e6f256e0ac2''
"""


def unique_id():
    return str(uuid.uuid4()).replace('-', '')
