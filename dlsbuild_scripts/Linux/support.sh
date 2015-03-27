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
#   _svn_dir or _git_dir  : The directory in the VCS repo where the module is located.
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

build_dir=${_build_dir}/${_module}

# Checkout module
mkdir -p $build_dir || ReportFailure "Can not mkdir $build_dir"
cd $build_dir       || ReportFailure "Can not cd to $build_dir"

if [[ "${_svn_dir:-undefined}" == "undefined" ]] ; then
    if [ ! -d $_version ]; then
        git clone --depth=100 $_git_dir $_version   || ReportFailure "Can not clone  $_git_dir"
        ( cd $_version &&  git checkout $_version ) || ReportFailure "Can not checkout $_version"        
    elif [ "$_force" == "true" ] ; then
        rm -rf $_version                            || ReportFailure "Can not rm $_version"
        git clone $_git_dir $_version               || ReportFailure "Can not clone  $_git_dir"
        ( cd $_version && git checkout $_version )  || ReportFailure "Can not checkout $_version"
    else
        ( cd $_version && git fetch --tags && git checkout $_version ) ||
            ReportFailure "Directory $build_dir/$_version not up to date with $_svn_dir"
    fi
else
    if [ ! -d $_version ]; then
        svn checkout -q $_svn_dir $_version         || ReportFailure "Can not check out  $_svn_dir"
    elif [ "$_force" == "true" ] ; then
        rm -rf $_version                            || ReportFailure "Can not rm $_version"
        svn checkout -q $_svn_dir $_version         || ReportFailure "Can not check out  $_svn_dir"
    elif (( $(svn status -qu $_version | grep -Ev "^M.*configure/RELEASE$" | wc -l) != 1 )) ; then
        ReportFailure "Directory $build_dir/$_version not up to date with $_svn_dir"
    fi
fi

cd $_version                                        || ReportFailure "Can not cd to $_version"
if [ ! -f configure/RELEASE.vcs ] ; then
    cp configure/RELEASE configure/RELEASE.vcs
fi

if [[ "${_svn_dir:-undefined}" == "undefined" ]] ; then
    git cat-file -p HEAD:configure/RELEASE > configure/RELEASE.vcs
else
    # Write some history (Kludging a definition of SVN_ROOT)
    SVN_ROOT=http://serv0002.cs.diamond.ac.uk/repos/controls \
      dls-logs-since-release.py -r --area=$_area $_module > DEVHISTORY.autogen

    # Modify configure/RELEASE
    svn cat configure/RELEASE > configure/RELEASE.vcs
fi

rm configure/RELEASE

sed -e 's,^ *EPICS_BASE *=.*$,EPICS_BASE='$EPICS_BASE',' \
    -e 's,^ *SUPPORT *=.*$,SUPPORT=/dls_sw/prod/'$(echo $_epics | cut -d_ -f1)'/support,' \
    -e 's,^ *WORK *=.*$,#WORK=commented out to prevent prod modules depending on work modules,' configure/RELEASE.vcs > configure/RELEASE

cat > configure/RELEASE.${EPICS_HOST_ARCH} <<EOF
EPICS_BASE=${EPICS_BASE}
SUPPORT=/dls_sw/prod/$(echo $_epics | cut -d_ -f1)/support
EOF
cp configure/RELEASE.${EPICS_HOST_ARCH} configure/RELEASE.${EPICS_HOST_ARCH}.Common

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
    cat $error_log | mail -s "Build Errors: $_area $_module $_version" $_email
fi
