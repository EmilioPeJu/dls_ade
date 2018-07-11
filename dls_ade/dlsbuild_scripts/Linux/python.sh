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
#   _svn_dir or _git_dir  : The directory in the VCS repo where the module is
#                           located.
#   _module    : The module name
#   _version   : The module version
#   _area      : The build area
#   _force     : Force the build (i.e. rebuild even if already exists)
#   _build_name: The base name to use for log files etc.
#

# Uncomment the following for tracing
# set -o xtrace

# Set up environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
OS_VERSION=$(lsb_release -sr | cut -d. -f1)
# Ensure CA Repeater is running (will close itself if already running)
EPICS_CA_SERVER_PORT=5064 EPICS_CA_REPEATER_PORT=5065 caRepeater &
EPICS_CA_SERVER_PORT=6064 EPICS_CA_REPEATER_PORT=6065 caRepeater &

case "$OS_VERSION" in
    [45])
        build_dir=${_build_dir}/${_module}
        PREFIX=/dls_sw/prod/tools/RHEL$OS_VERSION
        PYTHON=${PREFIX}/bin/python2.6
        INSTALL_DIR=${PREFIX}/lib/python2.6/site-packages
        ;;
    [67])
        build_dir=${_build_dir}/RHEL${OS_VERSION}-$(uname -m)/${_module}
        PREFIX=${build_dir}/${_version}/prefix
        PYTHON=/dls_sw/prod/tools/RHEL${OS_VERSION}-$(uname -m)/defaults/bin/dls-python
        INSTALL_DIR=${PREFIX}/lib/python2.7/site-packages
        TOOLS_DIR=/dls_sw/prod/tools/RHEL${OS_VERSION}-$(uname -m)
        ;;
       *)
        ReportFailure "OS Version ${OS_VERSION} not handled"
esac

SysLog debug "os_version=${OS_VERSION} python=${PYTHON} install_dir=${INSTALL_DIR} tools_dir=${TOOLS_DIR} prefix=${PREFIX} build_dir=${build_dir}"

# Checkout module
mkdir -p $build_dir || ReportFailure "Can not mkdir $build_dir"
cd $build_dir       || ReportFailure "Can not cd to $build_dir"

if [[ "${_svn_dir:-undefined}" == "undefined" ]] ; then
    if [ ! -d $_version ]; then
        SysLog info "Cloning repo: " $_git_dir
        git clone --depth=100 $_git_dir $_version   || ReportFailure "Can not clone  $_git_dir"
        SysLog info "checkout version tag: " $_version
        ( cd $_version && git checkout $_version ) || ReportFailure "Can not checkout $_version"
    elif [ "$_force" == "true" ] ; then
        SysLog info "Force: removing previous version: " ${PWD}/$_version
        rm -rf $_version                            || ReportFailure "Can not rm $_version"
        SysLog info "Cloning repo: " $_git_dir
        git clone --depth=100 $_git_dir $_version   || ReportFailure "Can not clone  $_git_dir"
        SysLog info "checkout version tag: " $_version
        ( cd $_version && git checkout $_version )  || ReportFailure "Can not checkout $_version"
    elif [[ (( $(git status -uno --porcelain | wc -l) != 0 )) ]]; then
        ReportFailure "Directory $build_dir/$_version not up to date with $_git_dir"
    fi
elif [[ "${_git_dir:-undefined}" == "undefined" ]] ; then
    if [ ! -d $_version ]; then
        svn checkout -q $_svn_dir $_version || ReportFailure "Can not check out  $_svn_dir"
    elif [ "$_force" == "true" ] ; then
        rm -rf $_version                    || ReportFailure "Can not rm $_version"
        svn checkout -q $_svn_dir $_version || ReportFailure "Can not check out  $_svn_dir"
    elif (( $(svn status -qu $_version | wc -l) != 1 )) ; then
        ReportFailure "Directory $build_dir/$_version not up to date with $_svn_dir"
    fi
else 
    ReportFailure "both _git_dir and _svn_dir are defined; unclear which to use"
fi

cd $_version || ReportFailure "Can not cd to $_version"

if [[ "${_svn_dir:-undefined}" != "undefined" ]] ; then
    # Write some history (Kludging a definition of SVN_ROOT)
    SVN_ROOT=http://serv0002.cs.diamond.ac.uk/repos/controls \
       dls-logs-since-release.py -r --area=$_area $_module > DEVHISTORY.autogen
fi

# Add Makefile.private
case "$OS_VERSION" in
    4)
        # Modify setup.py
        mv setup.py setup.py.vcs || ReportFailure "Can not move setup.py to setup.py.vcs"
        cat <<EOF > setup.py
# The following line was added by the release script
version = $(echo ${_version} | sed 's/-/./g')
EOF
        cat setup.py.vcs >> setup.py || ReportFailure "Can not edit setup.py"
        ;;
    *)
        cat <<EOF > Makefile.private || ReportFailure "Cannot write to Makefile.private"
# Overrides for release info
PREFIX = ${PREFIX}
PYTHON=${PYTHON}
INSTALL_DIR=${INSTALL_DIR}
SCRIPT_DIR=${PREFIX}/bin
MODULEVER = $(echo ${_version} | sed 's/-/./g')
EOF
esac

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
                SysLog info "Running make-defaults" $TOOLS_DIR $TOOLS_BUILD/RELEASE.RHEL$OS_VERSION-$(uname -m)
                $TOOLS_BUILD/make-defaults $TOOLS_DIR $TOOLS_BUILD/RELEASE.RHEL$OS_VERSION-$(uname -m)
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
