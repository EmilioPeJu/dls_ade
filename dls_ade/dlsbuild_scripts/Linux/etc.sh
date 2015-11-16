#!/usr/bin/env bash

# ******************************************************************************
# 
# Script to build a Diamond etc module
#
# This is a partial script which builds a module in for the dls-release system.
# The script is prepended with a list of variables before invocation by the
# dls-release mechanism. These variables are:
#
#   _email     : The email address of the user who initiated the build
#   _epics     : The DLS_EPICS_RELEASE to use
#   _build_dir : The parent directory in the file system in which to build the
#                module. This does not include module or version directories.
#   _svn_dir   : The directory in subversion where the module is located.
#   _module    : The module name
#   _version   : The module version
#   _area      : The build area
#   _force     : Force the build (i.e. rebuild even if already exists)
#   _build_name: The base name to use for log files etc.
#


ReportFailure()
{
    { [ -f "$1" ] && cat $1 || echo $*; } |
    mail -s "Build Errors: $_area $_module $_version"         $_email
    exit 2
}

# Set up environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
build_dir=${_build_dir}

# Checkout module
mkdir -p $build_dir                         || ReportFailure "Can not mkdir $build_dir"
cd $build_dir                               || ReportFailure "Can not cd to $build_dir"
if [ ! -d $_module ]; then
    svn checkout -q $_svn_dir $_module         || ReportFailure "Can not check out  $_svn_dir"
    cd $_module                             || ReportFailure "Can not cd to $_module"
else
    cd $_module                             || ReportFailure "Can not cd to $_module"
    svn switch $_svn_dir                    || ReportFailure "Can not switch to $_version"
fi

if [ -e Makefile ] ; then
    make clean
    make
fi
