"""Perform checks on the validity of a Python 3 module.
"""
from distutils.errors import DistutilsFileError
from setuptools.config import read_configuration
from packaging.requirements import Requirement
import sys

import git
from git.exc import InvalidGitRepositoryError
from pipfile import Pipfile


USAGE = '''{} [version]: check validity of Python 3 module.

Check that the version in setup.cfg matches a tag on the current commit.
If version is provided, check that it matches the version in setup.cfg.

Check that the dependencies in setup.cfg match those in Pipfile.
'''


def usage():
    print(USAGE.format(sys.argv[0]))


def compare_requirements(pipenv_reqs, setup_reqs):
    """Compare two different sets of requirements.

    Arguments:
        pipenv_reqs: list of name and specifier strings
        setup_reqs: list of name and specifier strings

    Returns:
        True if the requirements are compatible.
    """
    for pipenv_spec, setup_spec in zip(sorted(pipenv_reqs), sorted(setup_reqs)):
        pipenv_req = Requirement(pipenv_spec)
        setup_req = Requirement(setup_spec)
        if pipenv_req.name != setup_req.name:
            print('Requirements {} and {} do not match'.format(
                pipenv_req, setup_req
            ))
            return False
        # If setup.cfg has specifiers, they must match Pipfile exactly.
        if setup_req.specifier and setup_req.specifier != pipenv_req.specifier:
            print('Requirements {} and {} do not match'.format(
                pipenv_req, setup_req
            ))
            return False
    return True


def get_tags_on_head(repo):
    head = repo.head.commit
    matching_tags = []
    for tag in repo.tags:
        if tag.commit == head:
            matching_tags.append(tag.name)

    return matching_tags


def load_pipenv_requirements(pipfile):
    pipfile_data = Pipfile.load(pipfile).data
    pipenv_requirements = []
    for req in sorted(pipfile_data['default']):
        pipenv_requirements.append(req + pipfile_data['default'][req])

    return pipenv_requirements


def main():
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
        print('WARNING: no setup.cfg file found; checks cannot be made')
        # We can't check but we must allow the build to continue.
        sys.exit()
    try:
        pipenv_requirements = load_pipenv_requirements('Pipfile')
    except FileNotFoundError:
        print('ERROR: no Pipfile found. Package is not valid')
        sys.exit(1)
    try:
        repo = git.Repo('.')
    except InvalidGitRepositoryError:
        print('ERROR: no Git repository found. Package is not valid')
        sys.exit(1)

    # Compare requirements
    if not compare_requirements(pipenv_requirements, setup_requirements):
        print('setup.cfg requirements: {}'.format(sorted(setup_requirements)))
        print('Pipfile requirements: {}'.format(sorted(pipenv_requirements)))
        sys.exit('Requirements in setup.cfg and Pipfile do not match')
    # Compare versions
    head_tags = get_tags_on_head(repo)
    setup_version = conf_dict['metadata']['version']
    if setup_version not in head_tags:
        sys.exit('No tag on HEAD matches setup.cfg version {}'.format(
            setup_version
        ))
    if provided_version is not None:
        if not setup_version == provided_version:
            error = 'Release version {} does not match setup.cfg version {}.'
            sys.exit(error.format(provided_version, setup_version))
