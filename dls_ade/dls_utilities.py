import collections
import json
import os
from packaging import version
import re
from dls_ade.exceptions import ParsingError
from dls_ade.dlsbuild import default_server

GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")


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
    else:
        check = re.compile('[0-9]+\-[0-9]+(\-[0-9]+)?(dls[0-9]+(\-[0-9]+)?)?')

    result = check.search(tag)

    if result is None or result.group() != tag:
        return False

    return True


def parse_pipfilelock(pipfilelock, include_dev=False):
    """Parse the JSON in Pipfile.lock and return the package info as a dict.

    Args:
        pipfilelock: path to Pipfile.lock
        include_dev: whether to include dev packages

    Returns:
        dict: package name -> package details

    """
    with open(pipfilelock) as f:
        j = json.load(f, object_pairs_hook=collections.OrderedDict)
        packages = collections.OrderedDict(j['default'])
        if include_dev:
            packages.update(j['develop'])
        return packages

def python3_module_installed(module, version):
    """ Returns True if module is installed but False is module is not.

    Args:
        module: package name
        version: package version

    Returns:
        bool: True if successful False otherwise

    """
    TESTING_ROOT = os.getenv('TESTING_ROOT', '')
    os_version = default_server().replace('redhat', 'RHEL')
    OS_DIR = f'{TESTING_ROOT}/dls_sw/prod/python3/{os_version}'
    target_path = os.path.join(OS_DIR, module, version, 'prefix')
    return os.path.isdir(target_path)