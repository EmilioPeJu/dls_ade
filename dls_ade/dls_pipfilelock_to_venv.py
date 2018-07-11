import sys
import os
import venv
from collections import OrderedDict
from git import Repo
import json


def main():
 
    with open('Pipfile.lock') as f:
        j = json.load(f, object_pairs_hook=OrderedDict)
        packages = OrderedDict(j['default'])
        packages.update(j['develop'])
 
    with open('./venv/lib/python3.6/site-packages/paths.pth', 'w') as f:
        for package, contents in packages.items():
            f.write('/home/svz41317/testing-root/dls_sw/prod/python3/RHEL6-x86_64/{}/{}/prefix/lib/python3.6/site-packages\n'.format(package, contents['version'][2:]))


    venv.create('venv',system_site_packages=False, clear=False, symlinks=False, with_pip=False)
