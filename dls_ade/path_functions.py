import os
from dls_ade.exceptions import ParsingError

GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")


def remove_end_slash(path_string):

    if path_string and path_string.endswith('/'):
        path_string = path_string[:-1]

    return path_string


def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that the technical area is
    also provided.

    Args:
        area(str): Area of repository
        module(str): Module to check

    Raises:
        :class:`exceptions.ValueError`: Missing technical area under beamline

    """

    if area == "ioc" and len(module.split('/')) < 2:
        raise ParsingError("Missing technical area under beamline")
