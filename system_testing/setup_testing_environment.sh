#! /bin/bash

export GIT_ROOT_DIR="controlstest"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if [ $# -eq 1 ]
  then
    export PATH=$1/bin:$PATH
    export PYTHONPATH=$1/lib/python*/site-packages:$SCRIPT_DIR:$PYTHONPATH
  else
    echo "Usage: $0 <installation-prefix>"
    return 1
fi

dls-python push_required_repos.py
