#! /bin/bash

# Use controlstest instead of controls on gitolite
export GIT_ROOT_DIR="controlstest"
# Use specific EPICS version for list-releases tests in prod
export DLS_EPICS_RELEASE=R3.14.12.3

# Add system test library to path
export PYTHONPATH=$PYTHONPATH:`pwd`

# Make sure gitolite has require repositories for testing against
python push_required_repos.py
