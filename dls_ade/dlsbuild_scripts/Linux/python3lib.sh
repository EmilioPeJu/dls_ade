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


# Define environment


PYTHON=~/python3/bin/python3
OS_VERSION=RHEL$(lsb_release -sr | cut -d. -f1)-$(uname -m)
PYTHON_VERSION="python$($PYTHON -V | cut -d" " -f"2" | cut -d"." -f1-2)"

TESTING_ROOT=~/testing-root
CENTRAL_LOCATION=$TESTING_ROOT/dls_sw/prod/python3/$OS_VERSION
WORK_DIST_DIR=$TESTING_ROOT/dls_sw/work/python3/distributions
PROD_DIST_DIR=$TESTING_ROOT/dls_sw/prod/python3/distributions

export PATH=~/python3/bin:$PATH

# Work
# Copy wheel from work to prod folder

install_dist=false

for dist in $(ls $WORK_DIST_DIR);
do
    module="$(cut -d'-' -f1 <<<"$dist")"
    version="$(cut -d'-' -f2 <<<"$dist")"
    if [[ "$module" = "$_module" ]] && [[ "$version" = "$_version" ]] && [[ ! -f $PROD_DIST_DIR/$dist ]]; then
        cp $WORK_DIST_DIR/$dist $PROD_DIST_DIR/$dist
        install_dist=true
        break
    fi
done


if $install_dist; then
    prefix_location=$CENTRAL_LOCATION/$_module/$_version/prefix
    site_packages_location=$prefix_location/lib/$PYTHON_VERSION/site-packages
    specifier="$_module==$_version"
        if [[ ! -d $site_packages_location ]]; then
            pip install --ignore-installed --no-index --no-deps --find-links=$PROD_DIST_DIR --prefix=$prefix_location $specifier
        else
            echo "Package $specifier is already installed"
        fi
fi
