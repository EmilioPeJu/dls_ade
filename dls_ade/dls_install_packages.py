"""
Install packages from a wheel cache into a central package location, parsing information from Pipfile.lock.
Subprocesses are used deliberatelly as the reccommended way of executing pip programmatically according to pip manual(pip 10.0.1) 
"""

from collections import OrderedDict
import json
import subprocess
import sys
import os
import os.path
import shutil

TESTING_ROOT = '/home/svz41317/testing-root'
central_location = TESTING_ROOT+'/dls_sw/prod/python3/RHEL6-x86_64'
prod_wheel_dir = TESTING_ROOT+'/dls_sw/prod/python3/distributions'
work_wheel_dir = TESTING_ROOT+'/dls_sw/work/python3/distributions'


def main():
    
    cur_dir = os.getcwd()
    os.chdir(work_wheel_dir)
    for wheel in os.listdir(work_wheel_dir):
        shutil.copy(wheel, prod_wheel_dir)
    
    os.chdir(cur_dir)
    try:
        with open('Pipfile.lock') as f:
            j = json.load(f, object_pairs_hook=OrderedDict)
            packages = OrderedDict(j['default'])
            packages.update(j['develop'])
            for package, contents in packages.items():
                file_path='{}/dls_sw/prod/python3/RHEL6-x86_64/{}/{}/prefix/lib/python3.6/site-packages'.format(TESTING_ROOT, package, contents['version'][2:])
                if not os.path.exists(file_path):
                    subprocess.check_call([sys.executable,'-m','pip', 'install','--ignore-installed','--prefix='+central_location+'/'+package+'/'+contents['version'][2:]+'/prefix','--find-links='+prod_wheel_dir,'--no-index','--no-deps',package+contents['version']])
    except FileNotFoundError:
        sys.exit('Job aborted: Pipfile.lock was not found!')
    except subprocess.CalledProcessError as err:
        sys.exit('One or more wheels were not found:\n{0}'.format(err))
