"""Read Pipfile.lock and create a virtualenv including a path file

If all required packages are not installed, the virtualenv cannot be
correctly created, so report an error and quit.

This module must be run with the deployed version of Python 3.

"""
import os.path
import sys
import venv
import shutil
from dls_ade.dlsbuild import default_server
from dls_ade.dls_utilities import parse_pipfilelock


TESTING_ROOT = os.getenv('TESTING_ROOT', '')
OS_VERSION = default_server().replace('redhat', 'RHEL')
PYTHON_VERSION = f'python{sys.version_info[0]}.{sys.version_info[1]}'
OS_DIR = f'{TESTING_ROOT}/dls_sw/prod/python3/{OS_VERSION}'

path_list = []
absent_pkg_list = []
force = False
USAGE_MESSAGE = """Usage: {}

Run without arguments from a folder that contains the standard Pipfile.lock
or specify lockfile name eg package-version.Pipfile.lock
"""


def usage():
    print(USAGE_MESSAGE.format(sys.argv[0]))

def venv_command():
    venv.create('lightweight-venv', system_site_packages=True, clear=False,
                symlinks=False, with_pip=False)

def construct_pkg_path(_packages):
    for package, contents in _packages.items():
        version_string = contents['version']
        assert version_string.startswith('==')
        version = version_string[2:]
        file_path = '{}/{}/{}/prefix/lib/{}/site-packages'.format(
            OS_DIR, package, version, PYTHON_VERSION
        )
        path_list.append(file_path)

def find_missing_pkgs():
    for p in path_list:
        if not os.path.exists(p):
            absent_pkg_list.append(p)

def create_venv():
    if not absent_pkg_list:

        if not os.path.exists('lightweight-venv'):
            venv_command()
        elif os.path.exists('lightweight-venv') and force:
            shutil.rmtree('lightweight-venv')
            venv_command()
        else:
            sys.exit('lightweight-venv already present!')
        paths_file = f'./lightweight-venv/lib/{PYTHON_VERSION}/site-packages/dls-installed-packages.pth'
        with open(paths_file, 'w') as f:
            for path in path_list:
                f.write(path + '\n')
        print('lightweight-venv with dls-installed-packages.pth has been created successfully!')
    else:
        print('The following packages need to be installed:')
        print('\n'.join(absent_pkg_list))
        sys.exit(1)

def main():
    pipfilelock = 'Pipfile.lock'

    if '-h' in sys.argv or '--help' in sys.argv:
        usage()
        sys.exit(1)

    if '-f' in sys.argv or '--force' in sys.argv:
        global force
        force = True

    for argument in sys.argv:
        if 'Pipfile.lock' in argument:
            pipfilelock = argument

    try:
        packages = parse_pipfilelock(pipfilelock)
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')

    construct_pkg_path(packages)
    find_missing_pkgs()
    create_venv()
