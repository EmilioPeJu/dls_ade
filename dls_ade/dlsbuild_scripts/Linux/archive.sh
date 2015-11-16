#!/bin/env -i /bin/bash

# ******************************************************************************
# 
# Script to build a Diamond production module for support, ioc or matlab areas
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
    cat "$TEMP_LOG" |  mail -s "dls-tar-module.py ${_action} failure" $_email
    exit 2
}

__run_job()
{
    set -o xtrace

    TEMP_LOG="$(mktemp)"
    trap ReportFailure ERR
    trap 'rm -f "$TEMP_LOG"' EXIT
    set -o errexit

    {
        release_dir=${_build_dir}/${_module}
        archive=${_build_dir}/${_module}/${_version}.tar.gz

        if [ "${_action}" == "archive" ] ; then
            find ${release_dir}/${_version} -name O.\* -prune -exec rm -rf {} \;
            tar -czf  $archive -C  $release_dir ${_version}
            rm -rf ${release_dir}/${_version}
        else
            tar -xzpf $archive -C  $release_dir ${_version}
            rm -rf ${archive}
        fi
    } > "$TEMP_LOG" 2>&1
}

__run_job &
