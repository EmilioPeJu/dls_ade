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

# Set up DLS environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
OS_VERSION=$(lsb_release -sr | cut -d. -f1)
OS_ARCH_STRING=RHEL${OS_VERSION}-$(uname -m)
# Ensure CA Repeater is running (will close itself if already running)
EPICS_CA_SERVER_PORT=5064 EPICS_CA_REPEATER_PORT=5065 caRepeater &
EPICS_CA_SERVER_PORT=6064 EPICS_CA_REPEATER_PORT=6065 caRepeater &

build_dir=${_build_dir}/${_module}

PYTHON=/dls_sw/prod/tools/${OS_ARCH_STRING}/Python3/3-7-2/prefix/bin/dls-python3
PIP=/dls_sw/prod/tools/${OS_ARCH_STRING}/Python3/3-7-2/prefix/bin/pip3
PROD_DIST_DIR=/dls_sw/prod/python3/${OS_ARCH_STRING}/distributions

# Testing section, this will need correcting for the final version.
DLS_ADE_LOCATION=/dls_sw/work/python3/${OS_ARCH_STRING}/dls_ade
PFL_TO_VENV=${DLS_ADE_LOCATION}/prefix/bin/dls-pipfilelock-to-venv.py
export PYTHONPATH=${DLS_ADE_LOCATION}/prefix/lib/python3.7/site-packages
PY3_CHECK=${DLS_ADE_LOCATION}/prefix/bin/dls-python3-check.py


SysLog debug "os_version=${OS_VERSION} python=${PYTHON} install_dir=${INSTALL_DIR} tools_dir=${TOOLS_DIR} build_dir=${build_dir}"

# CHECKOUT MODULE
mkdir -p ${build_dir} || ReportFailure "Can not mkdir ${build_dir}"
cd ${build_dir} || ReportFailure "Can not cd to ${build_dir}"

if [[ ! -d ${_version} ]]; then
    CloneRepo
elif [[ "${_force}" == "true" ]] ; then
    SysLog info "Force: removing previous version: ${PWD}/${_version}"
    rm -rf $_version || ReportFailure "Can not rm ${_version}"
    CloneRepo
elif [[ (( $(git status -uno --porcelain | wc -l) != 0 )) ]]; then
    ReportFailure "Directory ${build_dir}/${_version} not up to date with ${_git_dir}"
fi

PYTHON_VERSION="python$(${PYTHON} -V | cut -d" " -f"2" | cut -d"." -f1-2)"
cd ${_version} || ReportFailure "Can not cd to ${_version}"

# BUILD MODULE
error_log=${_build_name}.err
build_log=${_build_name}.log
status_log=${_build_name}.sta

SysLog info "Starting build. Build log: ${PWD}/${build_log} errors: ${PWD}/${error_log}"
{
    {
        # Build phase 1 - Build a wheel and install in prefix, for app or library
        ${PY3_CHECK} ${_version} || ReportFailure "Python3 module check failed."
        echo "Building source distribution ..."
        ${PYTHON} setup.py sdist
        echo "Building wheel ..."
        ${PYTHON} setup.py bdist_wheel
        # If running on the build server, copy the wheel to the distributions directory.
        echo "PROD_DIST_DIR $PROD_DIST_DIR"
        if [[ -w ${PROD_DIST_DIR} ]]; then
            echo "Copying to ${PROD_DIST_DIR}"
            cp dist/* ${PROD_DIST_DIR}
        fi
        mkdir -p prefix/lib/${PYTHON_VERSION}/site-packages
        SITE_PACKAGES=$(pwd)/prefix/lib/${PYTHON_VERSION}/site-packages
        export PYTHONPATH=${PYTHONPATH}:${SITE_PACKAGES}

        # Build phase 2 - Create venv from Pipfile.lock on condition there is Pipfile.lock
        if [[ -e Pipfile.lock ]]; then
            # Use the -p argument to install pip, we'll need it.
            "${PFL_TO_VENV}" -p || ReportFailure "Dependencies not installed."
            echo ${SITE_PACKAGES} >> $(pwd)/lightweight-venv/lib/${PYTHON_VERSION}/site-packages/dls-installed-packages.pth
            source lightweight-venv/bin/activate
            pip install . --prefix=prefix --no-deps --disable-pip-version-check --no-warn-script-location
            # Remove the unneeded pip and setuptools once installation is complete.
            pip uninstall -y setuptools pip
        else
            "${PIP}" install . --prefix=prefix --no-deps
        fi
        # Redirect '2' (STDERR) to '1' (STDOUT) so it can be piped to tee
        # Redirect '1' (STDOUT) to '3' (a new file descriptor) to save it for later
    } 2>&1 1>&3 | tee ${error_log}  # copy STDERR to error log
    # Redirect '1' (STDOUT) of tee (STDERR from above) to build log
    # Redirect '3' (saved STDOUT from above) to build log
} 1>${build_log} 3>&1  # redirect STDOUT and STDERR to build log
