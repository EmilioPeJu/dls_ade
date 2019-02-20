"""
Reads Pipfile.lock, creates a paths.pth and a venv only if all packages are installed
"""

import sys
import os.path
import venv
from collections import OrderedDict
import json
from dls_ade.dlsbuild import default_server


TESTING_ROOT = os.getenv('TESTING_ROOT', "")
OS_VERSION = default_server().replace('redhat', 'RHEL')
PYTHON_VERSION = "python{}.{}".format(sys.version_info[0],sys.version_info[1])
OS_DIR = '{}/dls_sw/prod/python3/{}'.format(TESTING_ROOT, OS_VERSION)


def main():
 
    try:
        with open('Pipfile.lock') as f:
            j = json.load(f, object_pairs_hook=OrderedDict)
            packages = OrderedDict(j['default'])
            packages.update(j['develop'])
    except IOError:
        sys.exit('Job aborted: Pipfile.lock was not found!')

    path_list = []
    absent_pkg_list = []
    
    for package, contents in packages.items():
        version_string = contents['version']
        assert version_string.startswith('==')
        version = version_string[2:]
        file_path = '{}/{}/{}/prefix/lib/{}/site-packages'.format(
            OS_DIR, package, version, PYTHON_VERSION
        )
        path_list.append(file_path)

    for p in path_list:
        if not os.path.exists(p):
            absent_pkg_list.append(p)

    if not absent_pkg_list:
        
        if not os.path.exists('venv'):
            venv.create('venv', system_site_packages=True, clear=False,
                                        symlinks=False, with_pip=False)
        else:
            sys.exit('venv already present!')
        with open('./venv/lib/' + PYTHON_VERSION + '/site-packages/paths.pth', 'w') as f:
            for pl in path_list:
                f.write(pl + '\n')
        print('venv with path.pth has been created successfully!')
    else:
        print('The following packages need to be installed:')
        print(*absent_pkg_list, sep='\n')
        sys.exit(1)
