import sys
import os
import venv
from collections import OrderedDict
from git import Repo
import json

home_folder = '/home/svz41317'
filesystem_root = home_folder + '/testing-root'
central_location = filesystem_root + '/dls_sw/prod/python3/RHEL6-x86_64'

work_dir = central_location+'/testapp/1.0.0'
os.makedirs(work_dir)

Repo.clone_from(home_folder+'/gitolite/testapp', work_dir)
os.chdir(work_dir)

def _main():
    home_folder = '/home/svz41317'
    filesystem_root = home_folder + '/testing-root'
    central_location = filesystem_root + '/dls_sw/prod/python3/RHEL6-x86_64'

    with open('Pipfile.lock') as f:
        j = json.load(f, object_pairs_hook=OrderedDict)
        packages = OrderedDict(j['default'])
        packages.update(j['develop'])
 
    with open('paths.pth', 'w') as f:
        for package, contents in packages.items():
            f.write('/home/svz41317/testing-root/dls_sw/prod/python3/RHEL6-x86_64/{}/{}/prefix/lib/python3.6/site-packages\n'.format(package, contents['version'][2:]))


    venv.create('venv',system_site_packages=False, clear=False, symlinks=False, with_pip=False)

    os.makedirs('prefix/lib/python3.6/site-packages')

    os.rename('paths.pth', '/venv/lib/python3.6/site-packages/paths.pth')
