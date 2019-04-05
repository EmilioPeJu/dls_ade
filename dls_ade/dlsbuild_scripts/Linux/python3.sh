#!/bin/bash
# ******************************************************************************
# 
# Script to build a Diamond production module for support, ioc or matlab areas
#
# This is a partial script which builds a module in for the dls-release system.
# The script is prepended with a list of variables before invocation by the
# dls-release mechanism. These variables are:
#
#   _email     : The email address of the user who initiated the build
#   _user      : The username (fed ID) of the user who initiated the build
#   _epics     : The DLS_EPICS_RELEASE to use
#   _build_dir : The parent directory in the file system in which to build the
#                module. This does not include module or version directories.
#   _git_dir   : The Git URL to clone
#   _module    : The module name
#   _version   : The module version
#   _area      : The build area
#   _force     : Force the build (i.e. rebuild even if already exists)
#   _build_name: The base name to use for log files etc.
#

# Uncomment the following for tracing
# set -o xtrace

# don't let standard input block the script execution
exec 0</dev/null

# Set up environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
OS_VERSION=$(lsb_release -sr | cut -d. -f1)
# Ensure CA Repeater is running (will close itself if already running)
EPICS_CA_SERVER_PORT=5064 EPICS_CA_REPEATER_PORT=5065 caRepeater &
EPICS_CA_SERVER_PORT=6064 EPICS_CA_REPEATER_PORT=6065 caRepeater &


build_dir=${_build_dir}/RHEL${OS_VERSION}-$(uname -m)/${_module}
PREFIX=${build_dir}/${_version}/prefix

# Testing section, this will need correcting for the final version.
PYTHON=/dls_sw/work/tools/RHEL${OS_VERSION}-$(uname -m)/Python3/prefix/bin/dls-python3
PIP=/dls_sw/work/tools/RHEL${OS_VERSION}-$(uname -m)/Python3/prefix/bin/pip3
export TESTING_ROOT=/dls_sw/work/python3/test-root
DLS_ADE_LOCATION=/dls_sw/work/python3/RHEL${OS_VERSION}-$(uname -m)/dls_ade
PFL_TO_VENV=${DLS_ADE_LOCATION}/prefix/bin/dls-pipfilelock-to-venv.py
$PY3_CHECK=${DLS_ADE_LOCATION}/prefix/bin/dls-python3-check.py
export PYTHONPATH=${DLS_ADE_LOCATION}/prefix/lib/python3.7/site-packages


SysLog debug "os_version=${OS_VERSION} python=${PYTHON} install_dir=${INSTALL_DIR} tools_dir=${TOOLS_DIR} prefix=${PREFIX} build_dir=${build_dir}"

# CHECKOUT MODULE
mkdir -p $build_dir || ReportFailure "Can not mkdir $build_dir"
cd $build_dir       || ReportFailure "Can not cd to $build_dir"

if [ ! -d $_version ]; then
    CloneRepo
elif [ "$_force" == "true" ] ; then
    SysLog info "Force: removing previous version: ${PWD}/$_version"
    rm -rf $_version || ReportFailure "Can not rm $_version"
    CloneRepo
elif [[ (( $(git status -uno --porcelain | wc -l) != 0 )) ]]; then
    ReportFailure "Directory $build_dir/$_version not up to date with $_git_dir"
fi

# BUILD MODULE

PYTHON_VERSION="python$($PYTHON -V | cut -d" " -f"2" | cut -d"." -f1-2)"
prod_dist_dir=dls_sw/prod/python3/distributions

# Build phase 1 - Build a wheel and install in prefix, for app or library
cd $_version || ReportFailure "Can not cd to $_version"
$PY3_CHECK $_version || ReportFailure "Python3 module check failed."
$PYTHON setup.py bdist_wheel
cp dist/* $TESTING_ROOT/$prod_dist_dir
mkdir -p prefix/lib/$PYTHON_VERSION/site-packages
SITE_PACKAGES=$(pwd)/prefix/lib/$PYTHON_VERSION/site-packages    
export PYTHONPATH=$PYTHONPATH:$SITE_PACKAGES

# Build phase 2 - Create venv from Pipfile.lock on condition there is Pipfile.lock
if [[ -e Pipfile.lock ]]; then
    $PFL_TO_VENV || ReportFailure "Dependencies not installed."
    echo $SITE_PACKAGES >> $(pwd)/lightweight-venv/lib/$PYTHON_VERSION/site-packages/dls-installed-packages.pth
    source lightweight-venv/bin/activate
    # Use the python from the virtualenv so that the libraries installed
    # are available. We don't use pip as is not available in the virtualenv.
    python setup.py install --prefix=prefix
else
    # Use pip as it allows installing with no dependencies.
    $PIP install . --prefix=prefix --no-deps
fi
