#!/bin/bash

# ******************************************************************************
# 
# Script to build a Diamond etc module
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

# Set up environment
export PATH

case $_module in
    base)
        build_dir=${_build_dir}/${_epics%%_64}
        module load controls-tools  #  Required to get the tools util-linux/logger on the path
        ;;
    extensions)
        build_dir=${_build_dir}/${_epics%%_64}
        DLS_EPICS_RELEASE=${_epics}
        source /dls_sw/etc/profile
        ;;
    *)
        build_dir=${_build_dir}/${_epics%%_64}/extensions/src
        DLS_EPICS_RELEASE=${_epics}
        source /dls_sw/etc/profile
        ;;
esac

SysLog debug "Creating dir: " $build_dir
mkdir -p $build_dir                         || ReportFailure "Can not mkdir $build_dir"
cd $build_dir                               || ReportFailure "Can not cd to $build_dir"

export is_test=true # if is_test - can clone the entire repository; may be requesting an SHA hash
if  [[ "$_build_dir" = "/dls_sw/epics" ]] ; then
    is_test=false
fi

# If force, remove existing version directory (whether or not it exists)
if [ "$_force" == "true" ] ; then
    SysLog info "Force: removing previous version: " ${PWD}/$_module
   rm -rf $_module                           || ReportFailure "Could not rm $_module"
fi

# Clone module if it doesn't already exist
if [ ! -d $_module ]; then
    SysLog info "Cloning repo: $_git_dir into: $_module"
    if $is_test ; then
        git clone $_git_dir $_module
    else
        git clone --depth=100 $_git_dir $_module                            || ReportFailure "Can not clone $_git_dir"
    fi
fi

# Checkout module
cd $_module                                                         || ReportFailure "Could not cd to $_module"
SysLog info "checkout version tag: " $_version
if $is_test ; then
    git checkout $_version  || ReportFailure "Could not checkout $_version"
else
    ( git fetch --depth=1 origin tag $_version || git fetch origin tag $_version ) && git checkout $_version  || ReportFailure "Could not checkout $_version"
fi
# Build
error_log=${_build_name}.err
build_log=${_build_name}.log
SysLog info "Starting build. Build log: ${PWD}/${build_log} errors: ${PWD}/${error_log}"
{
    {
        make clean && make
        echo $? >${_build_name}.sta
    } 4>&1 1>&3 2>&4 |
    tee $error_log
} >$build_log 3>&1

if (( $(cat ${_build_name}.sta) != 0 )) ; then
    ReportFailure ${PWD}/$error_log
elif (( $(stat -c%s $error_log) != 0 )) ; then
    cat $error_log | mail -s "Build Errors: $_area $_module $_version" $_email
fi

SysLog info "Build complete"
