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
from dls_ade.dlsbuild import default_server
from dls_ade.dls_utilities import parse_pipfilelock


os_version = default_server().replace('redhat', 'RHEL')
python_version = "python{}.{}".format(sys.version_info[0],sys.version_info[1])
TESTING_ROOT = os.getenv('TESTING_ROOT', "")
WORK_DIST_DIR = TESTING_ROOT + '/dls_sw/work/python3/distributions'
CENTRAL_LOCATION = TESTING_ROOT + '/dls_sw/prod/python3/' + os_version
PIP_COMMAND = [sys.executable, '-m', 'pip', '--disable-pip-version-check', 
               'wheel', '--no-deps', '--wheel-dir='+ WORK_DIST_DIR]
missing_pkgs=[]
USAGE_MESSAGE = """Usage: {}

Reads Pipfile.lock and fetches wheels for all dependencies into the 
distribution directory. Runs without any arguments, on a folder with
Pipfile.lock
"""


def usage():
    print(USAGE_MESSAGE.format(sys.argv[0]))

def pkgs_to_install(_package, _version):

    prefix_location = os.path.join(CENTRAL_LOCATION, _package,
                                       _version[2:], 'prefix')
    site_packages_location = os.path.join(prefix_location,
                                          'lib/' + python_version + '/site-packages')
    if not os.path.isdir(site_packages_location):
        missing_pkgs.append(_package.replace('-','_')+' '+_version[2:])

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
            pkgs_to_install(package, version)
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')

    if missing_pkgs:
        print("\nEnter the following commands to install necessary dependencies:\n")
        for item in missing_pkgs:
            print("dls-release.py --python3lib -l " + item)
    else:
        print("All necessary dependencies are installed.")