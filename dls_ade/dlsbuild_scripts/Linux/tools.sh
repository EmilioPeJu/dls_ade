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
#   _svn_dir or _git_dir    : The directory in subversion where the module is
#                             located.
#   _module    : The module name
#   _version   : The module version
#   _area      : The build area
#   _force     : Force the build (i.e. rebuild even if already exists)
#   _build_name: The base name to use for log files etc.
#


ReportFailure()
{
    { [ -f "$1" ] && cat $1 || echo $*; } |
    mail -s "Build Errors: $_area $_module $_version" $_email
    exit 2
}


# Set up environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile

work_tar_dir=/dls_sw/work/targetOS/tar-files
prod_tar_dir=/dls_sw/prod/targetOS/tar-files
if [ ! -z "$(ls $work_tar_dir/)" -a -w $prod_tar_dir ]; then
    mv $work_tar_dir/* $prod_tar_dir || ReportFailure "Can not move tar files"
fi

# Ensure there is a architecture dependent build directory available
OS_VERSION=$(lsb_release -sr | cut -d. -f1)


TOOLS_BUILD=/dls_sw/prod/etc/build/tools_build
TOOLS_ROOT=/dls_sw/prod/tools/RHEL$OS_VERSION-$(uname -m)
build_dir=$_build_dir/RHEL$OS_VERSION-$(uname -m)

# Checkout module
mkdir -p $build_dir/${_module} || ReportFailure "Can not mkdir $build_dir/${_module}"
cd $build_dir/${_module} || ReportFailure "Can not cd to $build_dir/${_module}"

if [ ! -d $_version ]; then
    git clone --depth=100 $_git_dir $_version || ReportFailure "Can not clone  $_git_dir"
    ( cd $_version && git fetch --depth=1 origin tag $_version && git checkout $_version ) || ReportFailure "Can not checkout $_version"
elif [ "$_force" == "true" ] ; then
    rm -rf $_version                            || ReportFailure "Can not rm $_version"
    git clone --depth=100 $_git_dir $_version               || ReportFailure "Can not clone  $_git_dir"
    ( cd $_version && git fetch --depth=1 origin tag $_version && git checkout $_version )  || ReportFailure "Can not checkout $_version"
elif (( $(git status -uno --porcelain | grep -Ev "M.*configure/RELEASE$" | wc -l) != 0)) ; then
    ReportFailure "Directory $build_dir/$_version not up to date with $_git_dir"
fi

# Add the ROOT definition to the RELEASE file
release_file="$_version"/configure/RELEASE

# The following is for short term compatibility purposes
[ ! -f "$release_file" ] && release_file="$_version"/RELEASE

if [ -f "$release_file" ] ; then
    if (( ! $(grep -c '^( *ROOT| *TOOLS_SUPPORT)' "$release_file") )) ; then
        sed -i "1i\
TOOLS_SUPPORT=$TOOLS_ROOT" "$release_file"
    else
        sed -i \
            -e 's,^ *ROOT *=.*$,ROOT='"$TOOLS_ROOT," \
            -e 's,^ *TOOLS_SUPPORT *=.*$,TOOLS_SUPPORT='"$TOOLS_ROOT," \
            "$release_file"
    fi
fi

# Build
$TOOLS_BUILD/build_program -n $_build_name ${_version}

if (( $(cat ${_version}/${_build_name}.sta) != 0 )) ; then
    ReportFailure ${_version}/${_build_name}.log
fi

$TOOLS_BUILD/make-defaults $build_dir $TOOLS_BUILD/RELEASE.RHEL$OS_VERSION-$(uname -m)

