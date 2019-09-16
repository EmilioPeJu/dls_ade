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
#   _git_dir   : The Git URL to clone
#   _module    : The module name
#   _version   : The module version
#   _area      : The build area
#   _force     : Force the build (i.e. rebuild even if already exists)
#   _build_name: The base name to use for log files etc.
#

# Uncomment the following for tracing
# set -o xtrace

# don't let standard input block the script execution
exec 0</dev/null

# Set up environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
OS_VERSION=$(lsb_release -sr | cut -d. -f1)
# Ensure CA Repeater is running (will close itself if already running)
EPICS_CA_SERVER_PORT=5064 EPICS_CA_REPEATER_PORT=5065 caRepeater &
EPICS_CA_SERVER_PORT=6064 EPICS_CA_REPEATER_PORT=6065 caRepeater &

build_dir=${_build_dir}/${_module}
PREFIX=${build_dir}/${_version}/prefix
RHEL=RHEL${OS_VERSION}-$(uname -m)
PYTHON=/dls_sw/prod/tools/$RHEL/defaults/bin/dls-python
INSTALL_DIR=${PREFIX}/lib/python2.7/site-packages
TOOLS_DIR=/dls_sw/prod/tools/$RHEL

SysLog debug "os_version=${OS_VERSION} python=${PYTHON} install_dir=${INSTALL_DIR} tools_dir=${TOOLS_DIR} prefix=${PREFIX} build_dir=${build_dir}"

export is_test=true # if is_test - can clone the entire repository; may be requesting an SHA hash
if  [[ "$build_dir" =~ "/prod/" ]] ; then
    is_test=false
fi

# Checkout module
mkdir -p $build_dir || ReportFailure "Can not mkdir $build_dir"
cd $build_dir       || ReportFailure "Can not cd to $build_dir"

if [ ! -d $_version ]; then
    CloneRepo
elif [ "$_force" == "true" ] ; then
    SysLog info "Force: removing previous version: ${PWD}/$_version"
    rm -rf $_version || ReportFailure "Can not rm $_version"
    CloneRepo
elif [[ (( $(git status -uno --porcelain | wc -l) != 0 )) ]]; then
    ReportFailure "Directory $build_dir/$_version not up to date with $_git_dir"
fi

cd $_version || ReportFailure "Can not cd to $_version"


cat <<EOF > Makefile.private || ReportFailure "Cannot write to Makefile.private"
# Overrides for release info
PREFIX = ${PREFIX}
PYTHON=${PYTHON}
INSTALL_DIR=${INSTALL_DIR}
SCRIPT_DIR=${PREFIX}/bin
MODULEVER = $(echo ${_version} | sed 's/-/./g')
EOF

# Build
error_log=${_build_name}.err
build_log=${_build_name}.log
status_log=${_build_name}.sta
SysLog info "Starting build. Build log: ${PWD}/${build_log} errors: ${PWD}/${error_log}"
{
    {
        mkdir -p ${INSTALL_DIR}
        make clean && make
        echo $? >$status_log

        # This is a bit of a hack to only install in production builds
        if  [[ "$build_dir" =~ "/prod/" && "$(cat $status_log)" == "0" ]] ; then
            SysLog info "Doing make install in prod"
            make install
            echo $? >$status_log

            # If successful, run make-defaults
            if (( ! $(cat $status_log) )) ; then
                TOOLS_BUILD=/dls_sw/prod/etc/build/tools_build
                SysLog info "Running make-defaults" $TOOLS_DIR $TOOLS_BUILD/RELEASE.$RHEL
                $TOOLS_BUILD/make-defaults $TOOLS_DIR $TOOLS_BUILD/RELEASE.$RHEL
            fi
        fi
        # Redirect '2' (STDERR) to '1' (STDOUT) so it can be piped to tee
        # Redirect '1' (STDOUT) to '3' (a new file descriptor) to save it for later
    } 2>&1 1>&3 | tee $error_log  # copy STDERR to error log
    # Redirect '1' (STDOUT) of tee (STDERR from above) to build log
    # Redirect '3' (saved STDOUT from above) to build log
} 1>$build_log 3>&1  # redirect STDOUT and STDERR to build log

if (( $(cat $status_log) != 0 )) ; then
    ReportFailure ${PWD}/$error_log
elif (( $(stat -c%s $error_log) != 0 )) ; then
    cat $error_log | mail -s "Build Errors: $_area $_module $_version" $_email || SysLog err "Failed to email build errors"
elif [ -e documentation/Makefile ]; then
    SysLog info "Building documentation"
    make -C documentation || ReportFailure "Documentation build failed"
fi

SysLog info "Build complete"
