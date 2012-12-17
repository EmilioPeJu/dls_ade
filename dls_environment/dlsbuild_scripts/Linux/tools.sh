#!/bin/bash

# ******************************************************************************
# 
# Script to build a Diamond tools module.
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
    cat "$TEMP_LOG" |  mail -s "Build Errors: $_area $_module $_version" $_email
    exit 2
}

TEMP_LOG="$(mktemp)"
trap ReportFailure ERR
trap 'rm -f "$TEMP_LOG"' EXIT
set -o errexit
set -o xtrace

{
    # Set up environment
    DLS_EPICS_RELEASE=${_epics}
    source /dls_sw/etc/profile
    export SVN_ROOT=http://serv0002.cs.diamond.ac.uk/repos/controls

    work_tar_dir=/dls_sw/work/targetOS/tar-files
    prod_tar_dir=/dls_sw/prod/targetOS/tar-files
    if [ ! -z "$(ls $work_tar_dir/)" -a -w $prod_tar_dir ]; then
        mv $work_tar_dir/* $prod_tar_dir || { echo Can not move tar files; exit 1; }
    fi

    # Ensure there is a architecture dependent build directory available
    rhel_version=$(lsb_release -sr | cut -d. -f1)

    if (( $rhel_version < 6 )) ; then
        build_dir=$_build_dir/RHEL$rhel_version

        mkdir -p $build_dir
        cd $build_dir

        # Checkout build program - always from RHEL5 directory in branches
        if [ ! -d build_scripts ]; then
            svn checkout --depth=files $SVN_ROOT/diamond/branches/build_scripts/RHEL5 build_scripts
        else
            svn switch --depth=files $SVN_ROOT/diamond/branches/build_scripts/RHEL5 build_scripts 
        fi

        cd build_scripts

        [ "$_force" == "true" ] && rm -rf $_module

        if [ ! -d $_module ]; then
            svn checkout $_svn_dir $_module
        else
            svn switch $_svn_dir $_module
        fi

        ./build_program $_module
    else
        build_dir=$_build_dir/RHEL$rhel_version-$(uname -m)

        # Checkout module
        mkdir -p $build_dir/${_module}
        cd $build_dir/${_module}

        if [ ! -d $_version ]; then
            svn checkout $_svn_dir $_version
        elif [ "$_force" == "true" ] ; then
            rm -rf $_version
            svn checkout $_svn_dir $_version
        elif (( $(svn status -qu $_version | grep -Ev "^M.*configure/RELEASE$" | wc -l) != 1 )) ; then
            echo "Directory $build_dir/$_version not up to date with $_svn_dir"
            ReportFailure
        fi

        /dls_sw/prod/etc/build/tools_build/build_program ${_version}
    fi

} > "$TEMP_LOG" 2>&1
