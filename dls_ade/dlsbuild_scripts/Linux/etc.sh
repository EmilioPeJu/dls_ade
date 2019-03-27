#!/usr/bin/env bash

# *****************************************************************************
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

# don't let standard input block the script execution
exec 0</dev/null

# Set up environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
build_dir=${_build_dir}

SysLog info "Building etc in ${build_dir}"

# Checkout module
cd $build_dir                    || ReportFailure "Cannot cd to $build_dir"
cd $_module                      || ReportFailure "Cannot cd to $_module"
git pull --ff-only               || ReportFailure "Cannot pull latest version"

if [ -e Makefile ] ; then
    SysLog info "Running make"
    make                         || ReportFailure "make failed"
fi

SysLog info "Build complete"
