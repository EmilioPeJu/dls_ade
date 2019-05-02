"""
Get all the packages from PyPI and into a wheel cache under /dls_sw/work.
If a tar file is downloaded, this script will build a wheel. A list of
dependencies that need to be installed will be printed at the end.
Subprocesses are used deliberately as the recommended way of executing pip
programmatically according to the pip manual (pip 10.0.1).

"""
import logging
import os
import subprocess
import sys
from dls_ade.dls_utilities import parse_pipfilelock, python3_module_installed
from dls_ade import logconfig


WORK_DIST_DIR = '/dls_sw/work/python3/distributions'
TESTING_ROOT = os.getenv('TESTING_ROOT', '')
PIP_COMMAND = [sys.executable, '-m', 'pip', '--disable-pip-version-check',
               'wheel', '--no-deps']
USAGE_MESSAGE = """Usage: {}

Reads Pipfile.lock and fetches wheels for all dependencies into the 
distribution directory. Runs without any arguments, on a folder with
Pipfile.lock
"""

usermsg = logging.getLogger("usermessages")


def usage():
    print(USAGE_MESSAGE.format(sys.argv[0]))


def format_pkg_name(_package, _version):
    return '{} {}'.format(_package, _version[2:])


def populate_dist(_work_dist_dir):

    missing_pkgs = []

    try:
        packages = parse_pipfilelock('Pipfile.lock')
        for package, contents in packages.items():
            try:
                version = contents['version']
            except KeyError:
                error_msg = 'Failed to find a version for {} in Pipfile.lock'
                sys.exit(error_msg.format(package))
            specifier = package + version  # example: flask==1.0.2

            if not python3_module_installed(package, version[2:]):
                subprocess.check_call(PIP_COMMAND + [
                    '--wheel-dir=' + _work_dist_dir, specifier
                ])
                missing_pkgs.append(format_pkg_name(package, version))

        return missing_pkgs
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')


def main():
    logconfig.setup_logging(application='dls-populate-dist.py')

    if len(sys.argv) > 1:
        usage()
        sys.exit(1)

    work_dist_dir = os.path.join(TESTING_ROOT, WORK_DIST_DIR)
    pkgs_to_install = populate_dist(work_dist_dir)

    if pkgs_to_install:
        usermsg.info("\nEnter the following commands to "
                     "install necessary dependencies:\n")
        for item in pkgs_to_install:
            usermsg.info("dls-release.py --python3lib -l " + item)
    else:
        usermsg.info("All necessary dependencies are installed.")
