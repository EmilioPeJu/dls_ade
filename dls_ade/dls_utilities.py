import collections
import json
import os
from packaging import version
import re
from dls_ade.exceptions import ParsingError
from dls_ade.dlsbuild import default_server


GIT_ROOT_DIR = os.getenv('GIT_ROOT_DIR', "controls")
PIPFILELOCK = 'Pipfile.lock'


def testing_root():
    return os.getenv('TESTING_ROOT', '')


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


def normalise_name(name):
    """Normalise a python package name a la PEP 503.

    Note that this is copied from distlib; it is a 'vendored' library in a
    private package in pipenv, so I have copied the implementation.

    Args:
        name: package name

    Returns:
        normalised name

    """
    # https://www.python.org/dev/peps/pep-0503/#normalized-names
    return re.sub('[-_.]+', '-', name).lower()


def site_packages(prefix, python_version):
    """Return location of the site-packages directory

    Args:
        prefix: location of the bin and lib directories
        python_version: e.g. python2.7

    Returns:
        path to the site-packages directory
    """
    return os.path.join(prefix, 'lib', python_version, 'site-packages')


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


def python3_module_path(module, version):
    """
    Returns the actual path of the discovered module or None if module
    is not installed.

    Args:
        module: name of module
        version: version of module

    Returns:
        string: full file path
    """
    os_version = default_server().replace('redhat', 'RHEL')
    os_dir = '{}/dls_sw/prod/python3/{}'.format(
        testing_root(), os_version
    )
    released_modules = os.listdir(os_dir)
    for r in released_modules:
        normalised_name = normalise_name(r)
        if normalise_name(module) == normalised_name:
            module_dir = os.path.join(os_dir, r)
            target_path = os.path.join(module_dir, version)
            if os.path.isdir(target_path):
                return target_path
    return None


def python3_module_installed(module, version):
    """ Returns True if module is installed but False if module is not.

    This will check for the normalised package names, so if ABC-DEF is
    installed but abc_def is requested, this will return True.

    Args:
        module: name of module
        version: version of module

    Returns:
        bool: True if package exists, False otherwise

    """
    return python3_module_path(module, version) is not None

