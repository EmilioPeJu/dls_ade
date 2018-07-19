"""
Reads Pipfile.lock, creates a paths.pth and a venv only if all packages are installed
"""

import sys
import os.path
import venv
from collections import OrderedDict
from git import Repo
import json


TESTING_ROOT = '/home/svz41317/testing-root'


def main():
 
    try:
    	with open('Pipfile.lock') as f:
            j = json.load(f, object_pairs_hook=OrderedDict)
            packages = OrderedDict(j['default'])
            packages.update(j['develop'])
    except FileNotFoundError:
        sys.exit('Job aborted: Pipfile.lock was not found!')


    path_list = []
    pkg_not_found = False
    absent_pkg_list = []
    
    for package, contents in packages.items():
        version_string = contents['version']
        assert version_string.startswith('==')
        version = version_string[2:]
        file_path='{}/dls_sw/prod/python3/RHEL6-x86_64/{}/{}/prefix/lib/python3.6/site-packages'.format(TESTING_ROOT, package, version)
        path_list.append(file_path)

    for p in path_list:
        if not os.path.exists(p):
            pkg_not_found=True
            absent_pkg_list.append(p)

    if not pkg_not_found:
        
        if not os.path.exists('venv'):
            venv.create('venv',system_site_packages=True, clear=False, symlinks=False, with_pip=False)
        else:
            sys.exit('venv already present!')
        with open('./venv/lib/python3.6/site-packages/paths.pth', 'w') as f:
            for pl in path_list:
                f.write(pl +'\n')
        print('venv with path.pth has been created successfully!')
    else:
        print('The following packages need to be installed:')
        print(*absent_pkg_list, sep='\n')
        print("¯\_(ツ)_/¯")


    
