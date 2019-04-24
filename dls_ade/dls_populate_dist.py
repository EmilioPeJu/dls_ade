"""
Get all the packages from PyPI and into a wheel cache under /dls_sw/work.
If a tar file is downloaded, this script will build a wheel. A list of
dependencies that need to be installed will be printed at the end.
Subprocesses are used deliberately as the recommended way of executing pip
programmatically according to the pip manual (pip 10.0.1).

"""
import subprocess
import sys
import os
#from dls_ade.dlsbuild import default_server
from dls_ade.dls_utilities import parse_pipfilelock, python3_module_installed


TESTING_ROOT = os.getenv('TESTING_ROOT', '')
PIP_COMMAND = [sys.executable, '-m', 'pip', '--disable-pip-version-check',
               'wheel', '--no-deps']
USAGE_MESSAGE = """Usage: {}

Reads Pipfile.lock and fetches wheels for all dependencies into the 
distribution directory. Runs without any arguments, on a folder with
Pipfile.lock
"""


def usage():
    print(USAGE_MESSAGE.format(sys.argv[0]))


def format_pkg_name(_package, _version):
    return _package+' '+_version[2:]


def populate_dist(_work_dist_dir):

    missing_pkgs = []

    try:
        packages = parse_pipfilelock('Pipfile.lock')
        for package, contents in packages.items():
            try:
                version = contents['version']
            except KeyError as e:
                error_msg = 'Failed to find a version for {} in Pipfile.lock'
                sys.exit(error_msg.format(package))
            specifier = package + version  # example: flask==1.0.2

            if not python3_module_installed(package, version[2:]):
                subprocess.check_call(PIP_COMMAND + [
                    '--wheel-dir='+ _work_dist_dir, specifier
                ])
                missing_pkgs.append(format_pkg_name(package, version))

        return missing_pkgs
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')


def main():

    if len(sys.argv) > 1:
        usage()
        sys.exit(1)

    work_dist_dir = TESTING_ROOT + '/dls_sw/work/python3/distributions'
    pkgs_to_install = populate_dist(work_dist_dir)

    if pkgs_to_install:
        print("\nEnter the following commands to install necessary dependencies:\n")
        for item in pkgs_to_install:
            print("dls-release.py --python3lib -l " + item)
    else:
        print("All necessary dependencies are installed.")
