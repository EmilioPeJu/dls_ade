#! /bin/bash

export GIT_ROOT_DIR="controlstest"

if [ $# -eq 1 ]
  then
    export PATH=$1/dls_ade:$PATH
    export PYTHONPATH=$1:$1/systems_testing:$PYTHONPATH
fi
