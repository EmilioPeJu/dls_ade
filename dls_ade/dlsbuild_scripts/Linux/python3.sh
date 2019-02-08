#!/bin/bash

# Set up environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
OS_VERSION=$(lsb_release -sr | cut -d. -f1)
# Ensure CA Repeater is running (will close itself if already running)
EPICS_CA_SERVER_PORT=5064 EPICS_CA_REPEATER_PORT=5065 caRepeater &
EPICS_CA_SERVER_PORT=6064 EPICS_CA_REPEATER_PORT=6065 caRepeater &


build_dir=${_build_dir}/RHEL${OS_VERSION}-$(uname -m)/${_module}
PREFIX=${build_dir}/${_version}/prefix
PYTHON=/dls_sw/prod/tools/RHEL${OS_VERSION}-$(uname -m)/defaults/bin/dls-python


SysLog debug "os_version=${OS_VERSION} python=${PYTHON} install_dir=${INSTALL_DIR} tools_dir=${TOOLS_DIR} prefix=${PREFIX} build_dir=${build_dir}"

# CHECKOUT MODULE
mkdir -p $build_dir || ReportFailure "Can not mkdir $build_dir"
cd $build_dir       || ReportFailure "Can not cd to $build_dir"

if [[ "${_svn_dir:-undefined}" == "undefined" ]] ; then
    if [ ! -d $_version ]; then
        SysLog info "Cloning repo: " $_git_dir
        git clone --depth=100 $_git_dir $_version   || ReportFailure "Can not clone  $_git_dir"
        SysLog info "checkout version tag: " $_version
        ( cd $_version && git fetch --depth=1 origin tag $_version && git checkout $_version ) || ReportFailure "Can not checkout $_version"
    elif [ "$_force" == "true" ] ; then
        SysLog info "Force: removing previous version: " ${PWD}/$_version
        rm -rf $_version                            || ReportFailure "Can not rm $_version"
        SysLog info "Cloning repo: " $_git_dir
        git clone --depth=100 $_git_dir $_version   || ReportFailure "Can not clone  $_git_dir"
        SysLog info "checkout version tag: " $_version
        ( cd $_version && git fetch --depth=1 origin tag $_version && git checkout $_version )  || ReportFailure "Can not checkout $_version"
    elif [[ (( $(git status -uno --porcelain | wc -l) != 0 )) ]]; then
        ReportFailure "Directory $build_dir/$_version not up to date with $_git_dir"
    fi
elif [[ "${_git_dir:-undefined}" == "undefined" ]] ; then
    if [ ! -d $_version ]; then
        svn checkout -q $_svn_dir $_version || ReportFailure "Can not check out  $_svn_dir"
    elif [ "$_force" == "true" ] ; then
        rm -rf $_version                    || ReportFailure "Can not rm $_version"
        svn checkout -q $_svn_dir $_version || ReportFailure "Can not check out  $_svn_dir"
    elif (( $(svn status -qu $_version | wc -l) != 1 )) ; then
        ReportFailure "Directory $build_dir/$_version not up to date with $_svn_dir"
    fi
else 
    ReportFailure "both _git_dir and _svn_dir are defined; unclear which to use"
fi

# BUILD MODULE
# Testing section, necessary for running dls-pipfilelock-to-venv.py, comment out for production
export PATH=~/dls_ade/prefix/bin:$PATH
export PYTHONPATH=~/dls_ade/prefix/lib/python3.6/site-packages
export TESTING_ROOT=~/testing-root

# Create venv from Pipfile.lock
cd $_version || ReportFailure "Can not cd to $_version"
dls-pipfilelock-to-venv.py || ReportFailure "Dependencies not installed."

# Create prefix and install app using the its own venv
mkdir -p prefix/lib/python3.6/site-packages
SITE_PACKAGES=$(pwd)/prefix/lib/python3.6/site-packages
source  venv/bin/activate
export PYTHONPATH=$PYTHONPATH:$SITE_PACKAGES
echo $SITE_PACKAGES >> $(pwd)/venv/lib/python3.6/site-packages/paths.pth

# Install app - so that it is available from its own venv
python setup.py install --prefix=prefix
deactivate
echo "Script finished."
