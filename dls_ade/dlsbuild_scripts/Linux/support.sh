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

build_dir=${_build_dir}/${_module}

mkdir -p $build_dir || ReportFailure "Can not mkdir $build_dir"
cd $build_dir       || ReportFailure "Can not cd to $build_dir"

export is_test=true # if is_test - can clone the entire repository; may be requesting an SHA hash
if  [[ "$_build_dir" =~ "/prod/" ]] ; then
    is_test=false
fi

SysLog debug "version dir: " ${PWD}/$_version


if [ ! -d $_version ]; then
    CloneRepo
elif [ "$_force" == "true" ] ; then
    SysLog info "Force: removing previous version: ${PWD}/$_version"
    rm -rf $_version || ReportFailure "Can not rm $_version"
    CloneRepo
elif (( $(git status -uno --porcelain | grep -Ev "M.*configure/RELEASE$" | wc -l) != 0 )) ; then
    ReportFailure "Directory $build_dir/$_version not up to date with $_git_dir"
fi

cd $_version || ReportFailure "Can not cd to $_version"
if [ ! -f configure/RELEASE.vcs ] ; then
    cp configure/RELEASE configure/RELEASE.vcs
fi

git cat-file -p HEAD:configure/RELEASE > configure/RELEASE.vcs

rm configure/RELEASE

sed -e 's,^ *EPICS_BASE *=.*$,EPICS_BASE='$EPICS_BASE',' \
    -e 's,^ *SUPPORT *=.*$,SUPPORT=/dls_sw/prod/'$(echo $_epics | cut -d_ -f1)'/support,' \
    -e 's,^ *WORK *=.*$,#WORK=commented out to prevent prod modules depending on work modules,' configure/RELEASE.vcs > configure/RELEASE

cat > configure/RELEASE.${EPICS_HOST_ARCH} <<EOF
EPICS_BASE=${EPICS_BASE}
SUPPORT=/dls_sw/prod/$(echo $_epics | cut -d_ -f1)/support
EOF
cp configure/RELEASE.${EPICS_HOST_ARCH} configure/RELEASE.${EPICS_HOST_ARCH}.Common
SysLog debug "Wrote configure/RELEASE.${EPICS_HOST_ARCH}[.Common]: " $(cat configure/RELEASE.${EPICS_HOST_ARCH})

git ls-files configure/VERSION --error-unmatch 1>&/dev/null && ReportFailure "configure/VERSION must not be in version control"
mkdir -p configure
echo $_version > configure/VERSION

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
