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


# Testing section, this will need correcting for the final version.
OS_VERSION=RHEL$(lsb_release -sr | cut -d. -f1)-$(uname -m)
PYTHON=/dls_sw/work/tools/${OS_VERSION}/Python3/prefix/bin/dls-python3
PYTHON_VERSION="python$($PYTHON -V | cut -d" " -f"2" | cut -d"." -f1-2)"
DLS_ADE_LOCATION=/dls_sw/work/python3/${OS_VERSION}/dls_ade
PFL_TO_VENV=${DLS_ADE_LOCATION}/prefix/bin/dls-pipfilelock-to-venv.py
export PYTHONPATH=${DLS_ADE_LOCATION}/prefix/lib/$PYTHON_VERSION/site-packages

export TESTING_ROOT=/dls_sw/work/python3/test-root
CENTRAL_LOCATION=$TESTING_ROOT/dls_sw/prod/python3/$OS_VERSION
WORK_DIST_DIR=$TESTING_ROOT/dls_sw/work/python3/distributions
PROD_DIST_DIR=$TESTING_ROOT/dls_sw/prod/python3/distributions

export PATH=/dls_sw/work/tools/${OS_VERSION}/Python3/prefix/bin:$PATH


# Copy dist (and lockfile if there is one) from work to prod folder
install_dist=false
for dist in $(find $WORK_DIST_DIR -maxdepth 1 -iname $_module-$_version*); do
    cp $dist $PROD_DIST_DIR
    install_dist=true
done


# Installation of dependency
if $install_dist; then
    _module=${_module/_/-}
    prefix_location=$CENTRAL_LOCATION/$_module/$_version/prefix
    site_packages_location=$prefix_location/lib/$PYTHON_VERSION/site-packages
    specifier="$_module==$_version"

    # Check if there is Pipfile.lock to create venv
    if [[ ! -d $site_packages_location ]]; then
        pip3 install --ignore-installed --no-index --no-deps --find-links=$PROD_DIST_DIR --prefix=$prefix_location $specifier
        if [[ -f $PROD_DIST_DIR/$_module-$_version.Pipfile.lock ]]; then
            pipfilelock=$_module-$_version.Pipfile.lock
            cd $CENTRAL_LOCATION/$_module/$_version
            cp $PROD_DIST_DIR/$pipfilelock .
            $PFL_TO_VENV $pipfilelock || ReportFailure "Dependencies not installed."
            # Change header to the correct venv
            shebang='#!'
            new_header="$shebang$CENTRAL_LOCATION/$_module/$_version/venv/bin/python"
            for script in $(ls $prefix_location/bin); do
                sed -i "1 s|^.*$|$new_header|" $prefix_location/bin/$script
            done
        else
            echo "No Pipfile.lock is present"
        fi
    else
        ReportFailure "$_module-$_version is already installed in prod"
    fi
else
    ReportFailure "No matching distribution was found for $_module-$_version"
fi
