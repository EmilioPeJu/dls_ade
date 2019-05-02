"""Perform checks on the validity of a Python 3 module.
"""
import logging
import sys
import git
from distutils.errors import DistutilsFileError
from setuptools.config import read_configuration
from packaging.requirements import Requirement
from dls_ade.dls_utilities import normalise_name
from git.exc import InvalidGitRepositoryError
from pipfile import Pipfile
from dls_ade import logconfig


USAGE = '''{} [version]: check validity of Python 3 module.

Check that the version in setup.cfg matches a tag on the current commit.
If version is provided, check that it matches the version in setup.cfg.

Check that the dependencies in setup.cfg match those in Pipfile.
'''

VERSION_INVALID = '''Version string '{}' is invalid.
Please use PEP-440-compliant versions.'''

REQUIREMENTS_INVALID = '''Requirements in setup.cfg and Pipfile do not match.
setup.cfg requirements: {}
Pipfile requirements: {}'''

NO_MATCHING_TAG = 'No tag on HEAD matches setup.cfg version {}'

VERSION_MISMATCH = 'Release version {} does not match setup.cfg version {}.'


usermsg = logging.getLogger("usermessages")


def usage():
    print(USAGE.format(sys.argv[0]))


def compare_requirements(reqs1, reqs2):
    """Compare two different sets of requirements.

    Arguments:
        reqs1: list of name and specifier strings
        reqs2: list of name and specifier strings

    Returns:
        True if the requirements are compatible.
    """
    if not len(reqs1) == len(reqs2):
        return False
    for spec1, spec2 in zip(sorted(reqs1), sorted(reqs2)):
        req1 = Requirement(spec1)
        req2 = Requirement(spec2)
        # Allow variants of module name in the same way as PyPI and Pipenv.
        if (normalise_name(req1.name) != normalise_name(req2.name) or
                req1.specifier != req2.specifier):
            return False
    return True


def get_tags_on_head(repo):
    """Return all the tags on the HEAD of a GitPython repo.

    Args:
        GitPython Repo object

    Returns:
        list of all the tag names that are attached to the HEAD commit
    """
    head = repo.head.commit
    matching_tags = []
    for tag in repo.tags:
        if tag.commit == head:
            matching_tags.append(tag.name)

    return matching_tags


def load_pipenv_requirements(pipfile):
    """Load the required packages from Pipfile.

    Load only the packages section, not the dev-packages section.

    Args:
        pipfile: path to Pipfile

    Returns
        list of specifiers e.g. numpy, scipy>=1.0.0
    """
    pipfile_data = Pipfile.load(pipfile).data
    pipenv_requirements = []
    default_requirements = pipfile_data['default']
    for package, version_specifier in default_requirements.items():
        requirement = package  # e.g. 'scipy'
        # Asterisk in Pipfile equals no identifier in setup.cfg.
        if version_specifier != '*':
            requirement += version_specifier  # e.g. 'scipy>=1.0.0'
        pipenv_requirements.append(requirement)

    return pipenv_requirements


def main():
    logconfig.setup_logging(application='dls-python3-check.py')
    provided_version = None
    if len(sys.argv) > 1:
        if sys.argv[1] in ('-h', '--help'):
            usage()
            sys.exit()
        else:
            provided_version = sys.argv[1]

    # Load data
    try:
        conf_dict = read_configuration('setup.cfg')
        setup_requirements = sorted(
            conf_dict['options'].get('install_requires', [])
        )
    except DistutilsFileError:
        usermsg.warning('No setup.cfg file found; checks cannot be made')
        # We can't check but we must allow the build to continue.
        sys.exit()
    try:
        pipenv_requirements = load_pipenv_requirements('Pipfile')
    except FileNotFoundError:
        usermsg.error('No Pipfile found. Package is not valid')
        sys.exit(1)
    try:
        repo = git.Repo('.')
    except InvalidGitRepositoryError:
        usermsg.error('No Git repository found. Package is not valid')
        sys.exit(1)

    # Compare requirements
    if not compare_requirements(pipenv_requirements, setup_requirements):
        sys.exit(REQUIREMENTS_INVALID.format(
            sorted(setup_requirements),
            sorted(pipenv_requirements)
        ))
    # Compare versions
    head_tags = get_tags_on_head(repo)
    setup_version = conf_dict['metadata']['version']
    if '.' not in setup_version:
        sys.exit(VERSION_INVALID.format(setup_version))
    if setup_version not in head_tags:
        sys.exit(NO_MATCHING_TAG.format(setup_version))
    if provided_version is not None:
        if not setup_version == provided_version:
            sys.exit(VERSION_MISMATCH.format(provided_version, setup_version))
