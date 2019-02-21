"""
Get all the packages from PyPI and into a wheel cache under /dls_sw/work.
If a tar file is downloaded, this script will build a wheel.
Subprocesses are used deliberately as the recommended way of executing pip
programmatically according to the pip manual (pip 10.0.1).

"""
import subprocess
import sys
import os
from dls_ade.dls_utilities import parse_pipfilelock


TESTING_ROOT = os.getenv('TESTING_ROOT', "")
WORK_DIST_DIR = TESTING_ROOT + '/dls_sw/work/python3/distributions' 
PIP_COMMAND = [sys.executable, '-m', 'pip', '--disable-pip-version-check', 
               'wheel', '--no-deps', '--wheel-dir='+ WORK_DIST_DIR]
USAGE_MESSAGE = """Usage: {}

Reads Pipfile.lock and fetches wheels for all dependencies into the 
distribution directory. Runs without any arguments, on a folder with
Pipfile.lock
"""


def usage():
    print(USAGE_MESSAGE.format(sys.argv[0]))


def main():

    if len(sys.argv) > 1:
        usage()
        sys.exit(1)

    try:
        packages = parse_pipfilelock('Pipfile.lock')
        for package, contents in packages.items():
            version = contents['version']
            specifier = package + version  # example: flask==1.0.2
            subprocess.check_call(PIP_COMMAND + [specifier])
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')
