#! /bin/bash

export GIT_ROOT_DIR="controlstest"

if [ $# -eq 1 ]
  then
    export PATH=$1/prefix/bin:$PATH
    export PYTHONPATH=$1:$PYTHONPATH
fi
