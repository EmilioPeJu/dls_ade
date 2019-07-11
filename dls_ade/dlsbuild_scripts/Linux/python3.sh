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
# e.g. RHEL7-x86_64
OS_ARCH_STRING=RHEL$(lsb_release -sr | cut -d. -f1)-$(uname -m)
# Ensure CA Repeater is running (will close itself if already running)
EPICS_CA_SERVER_PORT=5064 EPICS_CA_REPEATER_PORT=5065 caRepeater &
EPICS_CA_SERVER_PORT=6064 EPICS_CA_REPEATER_PORT=6065 caRepeater &

build_dir=${_build_dir}/${_module}

PROD_DIST_DIR=/dls_sw/prod/python3/${OS_ARCH_STRING}/distributions

SysLog debug "os_version=${OS_ARCH_STRING} python=$(which dls-python3) install_dir=${INSTALL_DIR} tools_dir=${TOOLS_DIR} build_dir=${build_dir}"

# CHECKOUT MODULE
mkdir -p ${build_dir} || ReportFailure "Can not mkdir ${build_dir}"
cd ${build_dir} || ReportFailure "Can not cd to ${build_dir}"

if [[ ! -d ${_version} ]]; then
    CloneRepo
elif [[ "${_force}" == "true" ]] ; then
    SysLog info "Force: removing previous version: ${PWD}/${_version}"
    rm -rf ${_version} || ReportFailure "Can not rm ${_version}"
    CloneRepo
elif [[ (( $(git status -uno --porcelain | wc -l) != 0 )) ]]; then
    ReportFailure "Directory ${build_dir}/${_version} not up to date with ${_git_dir}"
fi

PYTHON_VERSION="python$(dls-python3 -V | cut -d" " -f"2" | cut -d"." -f1-2)"
cd ${_version} || ReportFailure "Can not cd to ${_version}"

# BUILD MODULE
error_log=${_build_name}.err
build_log=${_build_name}.log
status_log=${_build_name}.sta

SysLog info "Starting build. Build log: ${PWD}/${build_log} errors: ${PWD}/${error_log}"
{
    # Create a subshell. Because we pipe the output of this section a subshell
    # is created anyway, so we might as well make it explicit.
    (
        # Build phase 1 - Build a wheel and install in prefix, for app or library
        if ! dls-py3 check ${_version}; then
            echo -e "\nPython 3 check failed." >&2
            echo 1 >${status_log}
            exit  # the subshell
        fi
        echo "Building source distribution ..."
        dls-python3 setup.py sdist
        echo "Building wheel ..."
        dls-python3 setup.py bdist_wheel
        # If running on the build server, copy the wheel to the distributions directory.
        if [[ -w ${PROD_DIST_DIR} ]]; then
            echo "Copying distribution files to ${PROD_DIST_DIR}"
            cp dist/* ${PROD_DIST_DIR}
        fi

        # Build phase 2:
        # - if a Pipfile.lock is committed, use it to create a virtualenv.
        #   That virtualenv can be used to run any command-line scripts.
        # - if no Pipfile.lock is committed, just install into prefix
        #   with no dependencies.
        if [[ -e Pipfile.lock ]]; then
            # Create the lightweight virtualenv.
            # Use the -p argument to install pip into the virtualenv, we'll need it.
            if ! dls-py3 pipfilelock-to-venv -p; then
                echo -e "\nCreating lightweight virtualenv failed." >&2
                echo 1 >${status_log}
                exit  # the subshell
            fi
            # Install this module into prefix using the virtualenv.
            source lightweight-venv/bin/activate
            pip install . --prefix=prefix --no-deps --disable-pip-version-check --no-warn-script-location
            echo $? >${status_log}
            # Remove the unneeded pip and setuptools once installation is complete.
            pip uninstall -y setuptools pip
            # Ensure that this module, installed in the prefix directory,
            # is available to the python installed in the lightweight
            # virtualenv.
            PREFIX_SITE_PACKAGES=$(pwd)/prefix/lib/${PYTHON_VERSION}/site-packages
            VENV_SITE_PACKAGES=$(pwd)/lightweight-venv/lib/${PYTHON_VERSION}/site-packages
            echo ${PREFIX_SITE_PACKAGES} >> ${VENV_SITE_PACKAGES}/dls-installed-packages.pth
            # Deactivate the virtualenv.
            deactivate
        else
            pip3 install . --prefix=prefix --no-deps
            echo $? >${status_log}
        fi
        # Redirect '2' (STDERR) to '1' (STDOUT) so it can be piped to tee
        # Redirect '1' (STDOUT) to '3' (a new file descriptor) to save it for later
    ) 2>&1 1>&3 | tee ${error_log}  # copy STDERR to error log
    # Redirect '1' (STDOUT) of tee (STDERR from above) to build log
    # Redirect '3' (saved STDOUT from above) to build log
} 1>${build_log} 3>&1  # redirect STDOUT and STDERR to build log


if (( $(cat ${status_log}) != 0 )) ; then
    ReportFailure ${PWD}/${error_log}
elif (( $(stat -c%s ${error_log}) != 0 )) ; then
    echo >> ${error_log}
    echo "These errors were generated by a python3 build." >> ${error_log}
    echo "The exit status was 0 so the build itself succeeded." >> ${error_log}
    cat ${error_log} | mail -s "Errors from successful build: ${_area} ${_module} ${_version}" $_email || SysLog err "Failed to email build errors"
fi

SysLog info "Build complete"
