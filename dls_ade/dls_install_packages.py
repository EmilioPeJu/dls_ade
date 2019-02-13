"""
Install packages from a wheel cache into a central package location, parsing information from Pipfile.lock.
Subprocesses are used deliberatelly as the reccommended way of executing pip programmatically according to pip manual(pip 10.0.1) 
"""

from collections import OrderedDict
import json
import logging
import subprocess
import sys
import os
import os.path
import shutil
from dls_ade.dlsbuild import default_server


os_version = default_server().replace('redhat', 'RHEL')
TESTING_ROOT = os.getenv('TESTING_ROOT', "")
central_location = TESTING_ROOT + '/dls_sw/prod/python3/' + os_version
prod_dist_dir = TESTING_ROOT + '/dls_sw/prod/python3/distributions'
work_dist_dir = TESTING_ROOT + '/dls_sw/work/python3/distributions'


def main():
    
    for wheel in os.listdir(work_dist_dir):
        work_wheel_path = os.path.join(work_dist_dir, wheel)
        prod_wheel_path = os.path.join(prod_dist_dir, wheel)
        if not os.path.exists(prod_wheel_path):
            logging.info('Copying file {} from work to prod'.format(wheel))
            shutil.copy(work_wheel_path, prod_dist_dir)
    
    try:
        with open('Pipfile.lock') as f:
            j = json.load(f, object_pairs_hook=OrderedDict)
            packages = OrderedDict(j['default'])
            packages.update(j['develop'])
            for package, contents in packages.items():
                # specifier is package and version e.g. flask==1.0.2
                specifier = package + contents['version']
                # Remove '==' from start of version string e.g. 1.0.2
                version = contents['version'][2:]
                prefix_location = os.path.join(central_location, package, version, 'prefix')               
                site_packages_location = os.path.join(prefix_location, 'lib/python3.6/site-packages')
                if not os.path.exists(site_packages_location):
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--ignore-installed', 
                                           '--prefix=' + prefix_location, '--find-links=' + prod_dist_dir,
                                           '--no-index', '--no-deps', specifier])
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')
    except subprocess.CalledProcessError as err:
        sys.exit('One or more wheels were not found:\n{0}'.format(err))
