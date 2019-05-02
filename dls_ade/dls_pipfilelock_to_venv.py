"""Read Pipfile.lock and create a virtualenv including a path file

If all required packages are not installed, the virtualenv cannot be
correctly created, so report an error and quit.

This module must be run with the deployed version of Python 3.

"""
import logging
import os.path
import shutil
import sys
import venv
from dls_ade.dlsbuild import default_server
from dls_ade.dls_utilities import parse_pipfilelock, python3_module_path
from dls_ade import logconfig


TESTING_ROOT = os.getenv('TESTING_ROOT', '')
OS_VERSION = default_server().replace('redhat', 'RHEL')
PYTHON_VERSION = f'python{sys.version_info[0]}.{sys.version_info[1]}'
OS_DIR = f'{TESTING_ROOT}/dls_sw/prod/python3/{OS_VERSION}'
VENV_NAME = 'lightweight-venv'
PATHS_FILENAME = 'dls-installed-packages.pth'
PATHS_FILE = f'{VENV_NAME}/lib/{PYTHON_VERSION}/site-packages/{PATHS_FILENAME}'

USAGE_MESSAGE = """Usage: {}

Run without arguments from a folder that contains the standard Pipfile.lock
or specify lockfile name eg package-version.Pipfile.lock
Force lightweight-venv installation with '-f' or '--force'
Create a lightweight-venv that includes pip with '-p' or '--pip'
"""

usermsg = logging.getLogger("usermessages")


def usage():
    print(USAGE_MESSAGE.format(sys.argv[0]))


def venv_command(with_pip):
    venv.create(VENV_NAME, system_site_packages=True, clear=False,
                symlinks=False, with_pip=with_pip)


def construct_pkg_path(_packages):
    path_list = []
    missing_pkgs = []
    for package, contents in _packages.items():
        version_string = contents['version']
        assert version_string.startswith('==')
        version = version_string[2:]
        file_path = python3_module_path(package, version)
        if file_path is None:
            missing_module = '{} {}'.format(package, version)
            missing_pkgs.append(missing_module)
        else:
            site_packages_path = f'prefix/lib/{PYTHON_VERSION}/site-packages'
            path_list.append(os.path.join(file_path, site_packages_path))
    return path_list, missing_pkgs


def create_venv(_path_list, _include_pip, _force):
    if not os.path.exists(VENV_NAME):
        venv_command(_include_pip)
    elif os.path.exists(VENV_NAME) and _force:
        shutil.rmtree(VENV_NAME)
        venv_command(_include_pip)
    else:
        sys.exit('lightweight-venv already present!')
    with open(PATHS_FILE, 'w') as f:
        for path in _path_list:
            f.write(path + '\n')
    usermsg.info('lightweight-venv has been created successfully!')


def main():
    logconfig.setup_logging(application='dls-pipfilelock-to-venv.py')
    include_pip = False
    force = False
    pipfilelock = 'Pipfile.lock'

    if '-h' in sys.argv or '--help' in sys.argv:
        usage()
        sys.exit(1)

    if '-f' in sys.argv or '--force' in sys.argv:
        force = True

    if '-p' in sys.argv or '--pip' in sys.argv:
        include_pip = True

    for argument in sys.argv:
        if 'Pipfile.lock' in argument:
            pipfilelock = argument

    try:
        packages = parse_pipfilelock(pipfilelock)
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')

    path_list, missing_pkgs = construct_pkg_path(packages)
    if missing_pkgs:
        usermsg.info('The following packages need to be installed:')
        usermsg.info('\n'.join(missing_pkgs))
        sys.exit(1)
    else:
        create_venv(path_list, include_pip, force)
