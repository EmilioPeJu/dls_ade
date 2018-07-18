"""
Get all the package wheels from PyPI and into a wheel cache under /work
Subprocesses are used deliberatelly as the reccommended way of executing pip programmatically according to pip manual(pip 10.0.1) 
"""

from collections import OrderedDict
import json
import subprocess
import sys

TESTING_ROOT = '/home/svz41317/testing-root'
work_wheel_dir = TESTING_ROOT+'/dls_sw/work/python3/distributions' 


def main():

    try:    
        with open('Pipfile.lock') as f:
            j = json.load(f, object_pairs_hook=OrderedDict)
            packages = OrderedDict(j['default'])
            packages.update(j['develop'])
            for package, contents in packages.items():
                version = contents['version']
                subprocess.check_call([sys.executable,'-m','pip','wheel','--no-deps','--wheel-dir='+work_wheel_dir,package+version])    
    except FileNotFoundError:
        sys.exit('Job aborted: Pipfile.lock was not found!')
  
        
