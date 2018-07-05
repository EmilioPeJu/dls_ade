#! /bin/bash

export GIT_ROOT_DIR="controlstest"

if [ $# -eq 3 ]
  then
    export PATH=$1:$PATH
    export PYTHONPATH=$2:$3:$PYTHONPATH
  else
    echo Please give the /bin, the site-packages folder and the system_testing folder paths.
    return 1
fi

dls-python push_required_repos.py
