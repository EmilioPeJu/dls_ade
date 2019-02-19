"""
Get all the packages from PyPI and into a wheel cache under /dls_sw/work.
If a tar file is downloaded, this script will build a wheel.
Subprocesses are used deliberatelly as the reccommended way of executing pip 
programmatically according to pip manual(pip 10.0.1) 
"""

from collections import OrderedDict
import json
import subprocess
import sys
import os


TESTING_ROOT = os.getenv('TESTING_ROOT', "")
work_dist_dir = TESTING_ROOT + '/dls_sw/work/python3/distributions' 


USAGE_MESSAGE ="""Usage: {} 

Reads Pipfile.lock and fetches wheels for all dependencies into the 
distribution directory.
"""


def usage():
    print(USAGE_MESSAGE.format(sys.argv[0]))


def main():

    if len(sys.argv) > 1:
        usage()
        sys.exit(1)

    try:    
        with open('Pipfile.lock') as f:
            j = json.load(f, object_pairs_hook=OrderedDict)
            packages = OrderedDict(j['default'])
            packages.update(j['develop'])
            for package, contents in packages.items():
                version = contents['version']
                specifier = package + version  # example: flask==1.0.2
                subprocess.check_call([sys.executable, '-m', 'pip', 'wheel', '--no-deps', '--wheel-dir=' + work_dist_dir, specifier])    
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')

