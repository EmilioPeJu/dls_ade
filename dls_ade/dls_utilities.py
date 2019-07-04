import collections
import json
import os
from packaging import version
import re
from dls_ade.exceptions import ParsingError
from dls_ade.dlsbuild import default_server


GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")
PIPFILELOCK = 'Pipfile.lock'
PY3_ROOT_DIR = '/dls_sw/prod/python3'


def remove_end_slash(path_string):

    if path_string and path_string.endswith('/'):
        path_string = path_string[:-1]

    return path_string


def remove_git_at_end(path_string):

    if path_string and path_string.endswith('.git'):
        return path_string[:-4]

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


def check_tag_is_valid(tag, area=None):
    """
    Checks if a given tag is a valid tag.

    The traditional Diamond versioning is something like X-Y[-Z][dlsA[-B]]

    For Python 3 we are allowing any versions as permitted by PEP-440:

    https://www.python.org/dev/peps/pep-0440/

    Args:
        tag(str): proposed tag string
        area(str): area to check tag against

    Returns:
        bool: True if tag is valid, False if not

    """
    if area == 'python3':
        # VERBOSE allows you to ignore the comments in VERSION_PATTERN.
        check = re.compile(r"^{}$".format(version.VERSION_PATTERN), re.VERBOSE)
        result = check.search(tag)
    else:
        number = "[0-9]+"
        optional_number = "[0-9]*"

        regex_pieces = dict(
            u_v_w = "{u}\-{v}(\-{w})?".format(u=number, v=number, w=number),
            dls_x_y = "(dls{x}(\-{y})?)?".format(x=number, y=number),
            alpha_beta_z = "((alpha|beta){z})?".format(z=optional_number)
        )
        pattern = '^{u_v_w}{dls_x_y}{alpha_beta_z}$'.format(**regex_pieces)
        check = re.compile(pattern)
        result = check.match(tag)

    if result is None:
        return False

    return True

