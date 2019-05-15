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
# expand all globs even if they don't match everything
shopt -s nullglob

# Set up DLS environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
# Ensure CA Repeater is running (will close itself if already running)
EPICS_CA_SERVER_PORT=5064 EPICS_CA_REPEATER_PORT=5065 caRepeater &
EPICS_CA_SERVER_PORT=6064 EPICS_CA_REPEATER_PORT=6065 caRepeater &

OS_VERSION=RHEL$(lsb_release -sr | cut -d. -f1)-$(uname -m)

# e.g. python3.7
PYTHON_VERSION="python$(dls-python3 -V | cut -d" " -f"2" | cut -d"." -f1-2)"

# This can be corrected once configure-tool assigns a version to dls_ade.
DLS_ADE_LOCATION=/dls_sw/work/python3/${OS_VERSION}/dls_ade
PFL_TO_VENV=${DLS_ADE_LOCATION}/prefix/bin/dls-pipfilelock-to-venv.py
export PYTHONPATH=${DLS_ADE_LOCATION}/prefix/lib/${PYTHON_VERSION}/site-packages

WORK_DIST_DIR=/dls_sw/work/python3/${OS_VERSION}/distributions
PROD_DIST_DIR=/dls_sw/prod/python3/${OS_VERSION}/distributions

if  [[ "${_build_dir}" =~ "/prod/" ]] ; then
    is_test=false
else
    is_test=true
fi

# The same as the normalise_name function we use in Python.
function normalise_name() {
    local name="$1"
    local lower_name=${name,,}
    local lower_dash_name=${lower_name//_/-}
    echo ${lower_dash_name}
}

function match_dist() {
    local normalised_dist=$(normalise_name $(basename $1))
    if [[ ${normalised_dist} == ${normalised_module}*${_version}* ]] && \
       [[ ${normalised_dist} != *pipfile.lock ]]; then
        return 0
    else
        return 1
    fi
}

prod_distributions=()
work_distributions=()
pipfilelock=${_module}-${_version}.Pipfile.lock
normalised_module=$(normalise_name ${_module})
prod_pfl=${PROD_DIST_DIR}/${pipfilelock}
work_pfl=${WORK_DIST_DIR}/${pipfilelock}
specifier="${_module}==${_version}"

# Check for existing release.
for released_module in "${_build_dir}"/* ; do
    normalised_released_module=$(normalise_name $(basename ${released_module}))
    if [[ ${normalised_released_module} == ${normalised_module} ]]; then
        version_location="${released_module}/${_version}"
    fi
done

# Remove existing release if _force is true.
if [[ -d "${version_location}" ]]; then
    if [[ ${_force} == true ]]; then
        SysLog info "Force: removing previous version: ${version_location}"
        rm -rf "${version_location}"
    else
        ReportFailure "${version_location} is already installed."
    fi
else
    # Always install using the normalised name.
    version_location="${_build_dir}/${normalised_module}/${_version}"
fi

log=${version_location}/${_build_name}.log
mkdir -p $(dirname ${log})

# Locate matching distributions in prod and work.
for dist in "${PROD_DIST_DIR}"/* ; do
    if match_dist "${dist}"; then
        prod_distributions+=(${dist})
    fi
done

for dist in "${WORK_DIST_DIR}"/* ; do
    if match_dist "${dist}"; then
        work_distributions+=(${dist})
    fi
done

# Determine which files to use for installation.
if [[ ${is_test} == true ]]; then
    # Test build: use files in work if present, otherwise look in prod.
    if [[ ${#work_distributions[@]} -gt 0 ]]; then
        distributions=(${work_distributions[@]})
        links_dir=${WORK_DIST_DIR}
    elif [[ ${#prod_distributions[@]} -gt 0 ]]; then
        distributions=(${prod_distributions[@]})
        links_dir=${PROD_DIST_DIR}
    fi
    if [[ -f "${work_pfl}" ]]; then
        pfl="${work_pfl}"
    elif [[ -f "${prod_pfl}" ]]; then
        pfl="${prod_pfl}"
    fi
else
    # Production build: move files from work then build from prod.
    if [[ ${#work_distributions[@]} -gt 0 ]]; then
        if [[ ${_force} == ${true} ]]; then
            mv "${work_distributions[@]}" "${PROD_DIST_DIR}"
        else  # Set no-clobber option to mv
            mv -n "${work_distributions[@]}" "${PROD_DIST_DIR}" || \
            ReportFailure "Could not move ${work_distributions[@]} to ${PROD_DIST_DIR}"
        fi
    fi
    if [[ -f "${work_pfl}" ]]; then
        if [[ ${_force} == true ]]; then
            mv "${work_pfl}" "${PROD_DIST_DIR}"
        else
            mv -n "${work_pfl}" "${PROD_DIST_DIR}" || \
            ReportFailure "Could not move ${work_pfl} to ${PROD_DIST_DIR}"
        fi
        pfl="${prod_pfl}"
    else
        if [[ -v prod_pfl ]]; then
            pfl="${prod_pfl}"
        fi
    fi

    distributions=(${prod_distributions[@]})
    links_dir=${PROD_DIST_DIR}
fi

echo "Matching distributions ${distributions[@]}"

# Install the distribution.
if [[ ${#distributions[@]} -gt 0 ]]; then

    prefix_location="${version_location}/prefix"
    site_packages_location="${prefix_location}/lib/${PYTHON_VERSION}/site-packages"
    # Check if there is Pipfile.lock to create the lightweight venv first.
    # This will fail if necessary dependencies aren't installed.
    if [[ -v pfl ]]; then
        echo "Installing venv from $pfl"
        cd ${version_location}
        cp "${pfl}" .
        "${PFL_TO_VENV}" "${pipfilelock}" || ReportFailure "Dependencies not installed."
    else
        echo "No Pipfile.lock is present" >> ${log}
    fi

    pip3 install --ignore-installed --no-index --no-deps \
                    --find-links=${links_dir} --prefix=${prefix_location} \
                    ${specifier} >> ${log} 2>&1 || \
                    ReportFailure "Failed to install $?"
    if [[ -d lightweight-venv ]]; then
        # Change header to the correct venv
        shebang='#!'
        new_header="${shebang}${version_location}/lightweight-venv/bin/python"
        for script in ${prefix_location}/bin/* ; do
            sed -i "1 s|^.*$|${new_header}|" "${script}"
        done
    fi
else
    ReportFailure "No matching distribution was found for ${specifier}"
fi
