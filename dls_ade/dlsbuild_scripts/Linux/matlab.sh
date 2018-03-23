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
#   _svn_dir or _git_dir  : The directory in the VCS repo where the module is
#                           located.
#   _module    : The module name
#   _version   : The module version
#   _area      : The build area
#   _force     : Force the build (i.e. rebuild even if already exists)
#   _build_name: The base name to use for log files etc.
#

# Set up environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
build_dir=${_build_dir}/${_module}

# Checkout module
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
    elif (( $(git status -uno --porcelain | wc -l) != 0)) ; then
        ReportFailure "Directory $build_dir/$_version not up to date with $_git_dir"
    fi
elif [[ "${_git_dir:-undefined}" == "undefined" ]] ; then
    if [ ! -d $_version ]; then
        svn checkout -q $_svn_dir $_version || ReportFailure "Can not check out  $_svn_dir"
    elif [ "$_force" == "true" ] ; then
        rm -rf $_version                    || ReportFailure "Can not rm $_version"
        svn checkout -q $_svn_dir $_version || ReportFailure "Can not check out  $_svn_dir"
    elif (( $(svn status -qu "$_version" | wc -l) != 1 )) ; then
        ReportFailure "Directory $build_dir/$_version not up to date with $_svn_dir"
    fi
else 
    ReportFailure "both _git_dir and _svn_dir are defined; unclear which to use"
fi

cd $_version || ReportFailure "Can not cd to $_version"

if [[ "${_svn_dir:-undefined}" == "undefined" ]] ; then
    git cat-file -p HEAD:configure/RELEASE > configure/RELEASE.vcs
else
    # Write some history (Kludging a definition of SVN_ROOT)
    SVN_ROOT=http://serv0002.cs.diamond.ac.uk/repos/controls \
      dls-logs-since-release.py -r --area=$_area $_module > DEVHISTORY.autogen
fi

# Build
error_log=${_build_name}.err
build_log=${_build_name}.log
SysLog info "Starting build. Build log: ${PWD}/${build_log} errors: ${PWD}/${error_log}"
{
    {
        make
        echo $? >${_build_name}.sta
    } 4>&1 1>&3 2>&4 |
    tee $error_log
} >$build_log 3>&1

if (( $(cat ${_build_name}.sta) != 0 )) ; then
    ReportFailure ${PWD}/$error_log
elif (( $(stat -c%s $error_log) != 0 )) ; then
    cat $error_log | mail -s "Build Errors: $_area $_module $_version" $_email || SysLog err "Failed to email build errors"
fi

SysLog info "Build complete"
