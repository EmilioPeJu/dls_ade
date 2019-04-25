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
from dls_ade.dls_utilities import parse_pipfilelock, python3_module_installed, python3_module_path



TESTING_ROOT = os.getenv('TESTING_ROOT', '')
OS_VERSION = default_server().replace('redhat', 'RHEL')
PYTHON_VERSION = f'python{sys.version_info[0]}.{sys.version_info[1]}'
OS_DIR = f'{TESTING_ROOT}/dls_sw/prod/python3/{OS_VERSION}'

force = False
USAGE_MESSAGE = """Usage: {}

Run without arguments from a folder that contains the standard Pipfile.lock
or specify lockfile name eg package-version.Pipfile.lock
"""


def usage():
    print(USAGE_MESSAGE.format(sys.argv[0]))

def venv_command(_pip):
    venv.create('lightweight-venv', system_site_packages=True, clear=False,
                symlinks=False, with_pip=_pip)


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


def create_venv(_path_list, _pip):
        if not os.path.exists('lightweight-venv'):
            venv_command(_pip)
        elif os.path.exists('lightweight-venv') and force:
            shutil.rmtree('lightweight-venv')
            venv_command(_pip)
        else:
            sys.exit('lightweight-venv already present!')
        paths_file = f'./lightweight-venv/lib/{PYTHON_VERSION}/site-packages/dls-installed-packages.pth'
        with open(paths_file, 'w') as f:
            for path in _path_list:
                f.write(path + '\n')
        print('lightweight-venv with dls-installed-packages.pth has been created successfully!')


def main():
    pip = False
    pipfilelock = 'Pipfile.lock'

    if '-h' in sys.argv or '--help' in sys.argv:
        usage()
        sys.exit(1)

    if '-f' in sys.argv or '--force' in sys.argv:
        global force
        force = True

    if '-p' in sys.argv or '--pip' in sys.argv:
        pip = True

    for argument in sys.argv:
        if 'Pipfile.lock' in argument:
            pipfilelock = argument

    try:
        packages = parse_pipfilelock(pipfilelock)
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')

    path_list, missing_pkgs = construct_pkg_path(packages)
    if missing_pkgs:
        print('The following packages need to be installed:')
        print('\n'.join(missing_pkgs))
        sys.exit(1)
    else:
        create_venv(path_list, pip)
