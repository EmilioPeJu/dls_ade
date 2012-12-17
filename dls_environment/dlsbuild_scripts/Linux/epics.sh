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
export PATH
export SVN_ROOT=http://serv0002.cs.diamond.ac.uk/repos/controls

case $_module in
    base|extensions)
        build_dir=${_build_dir}/${_epics%%_64}
        ;;
    *)
        build_dir=${_build_dir}/${_epics%%_64}/extensions/src
        ;;
esac

# Checkout module
mkdir -p $build_dir                         || ReportFailure "Can not mkdir $build_dir"
cd $build_dir                               || ReportFailure "Can not cd to $build_dir"
[ "$_force" == "false" ] || rm -rf $_module || ReportFailure "Can not rm $_module"

if [ ! -d $_module ]; then
    svn checkout $_svn_dir $_module         || ReportFailure "Can not check out  $_svn_dir"
    cd $_module                             || ReportFailure "Can not cd to $_module"
else
    cd $_module                             || ReportFailure "Can not cd to $_module"
    svn switch $_svn_dir                    || ReportFailure "Can not switch to $_module"
fi

# Build
error_log=${_build_name}.err
build_log=${_build_name}.log
{
    {
        make clean && make
        echo $? >${_build_name}.sta
    } 4>&1 1>&3 2>&4 |
    tee $error_log
} >$build_log 3>&1

if (( $(cat ${_build_name}.sta) != 0 )) ; then
    ReportFailure $error_log
elif (( $(stat -c%s $error_log) != 0 )) ; then
    cat $error_log | mail -s "Build Errors: $_area $_module $_version"         $_email
fi
