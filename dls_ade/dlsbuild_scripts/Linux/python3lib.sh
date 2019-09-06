#!/bin/bash
# ******************************************************************************
#
# Script to build a Diamond production module for the python3lib area.
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
# expand all globs even if they don't match anything
shopt -s nullglob

# Set up DLS environment
DLS_EPICS_RELEASE=${_epics}
source /dls_sw/etc/profile
# e.g. RHEL7-x86_64
OS_ARCH_STRING=RHEL$(lsb_release -sr | cut -d. -f1)-$(uname -m)
# Ensure CA Repeater is running (will close itself if already running)
EPICS_CA_SERVER_PORT=5064 EPICS_CA_REPEATER_PORT=5065 caRepeater &
EPICS_CA_SERVER_PORT=6064 EPICS_CA_REPEATER_PORT=6065 caRepeater &

# e.g. python3.7
PYTHON_VERSION="python$(dls-python3 -V | cut -d" " -f"2" | cut -d"." -f1-2)"

WORK_DIST_DIR=/dls_sw/work/python3/${OS_ARCH_STRING}/distributions
PROD_DIST_DIR=/dls_sw/prod/python3/${OS_ARCH_STRING}/distributions

if  [[ "${_build_dir}" =~ "/prod/" ]] ; then
    is_test=false
else
    is_test=true
fi

# The same as the normalise_name function we use in Python:
# all characters to lower-case and swap underscores for hyphens.
function normalise_name() {
    local name="$1"
    local lower_name=${name,,}
    local lower_dash_name=${lower_name//_/-}
    echo ${lower_dash_name}
}

# Return 0 if the argument is a valid Python distribution name matching
# the variables ${normalised_module} and ${_version}.
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
# If Pipfile.lock is provided it should have the name
# ${_module}-${_version}.Pipfile.lock where _module and _version are the
# arguments to dls-release.py.
pipfilelock=${_module}-${_version}.Pipfile.lock
normalised_module=$(normalise_name ${_module})
prod_pfl=${PROD_DIST_DIR}/${pipfilelock}
work_pfl=${WORK_DIST_DIR}/${pipfilelock}
specifier="${_module}==${_version}"

error_log=${_build_name}.err
build_log=${_build_name}.log
status_log=${_build_name}.sta


SysLog info "Starting build. Build log: ${PWD}/${build_log} errors: ${PWD}/${error_log}"
{
    # Create a subshell. Because we pipe the output of this section a subshell
    # is created anyway, so we might as well make it explicit.
    (
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
                echo -e "${version_location} is already installed." >&2
                echo 1 >${status_log}
                exit  # the subshell
            fi
        else
            # Always install using the normalised name.
            version_location="${_build_dir}/${normalised_module}/${_version}"
        fi

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
                    if ! mv -n "${work_distributions[@]}" "${PROD_DIST_DIR}"; then
                        echo -e "Could not move ${work_distributions[@]} to ${PROD_DIST_DIR}" >&2
                        echo 1 >${status_log}
                        exit  # the subshell
                    fi
                fi
                # Look again for prod distributions after the move.
                for dist in "${PROD_DIST_DIR}"/* ; do
                    if match_dist "${dist}"; then
                        prod_distributions+=(${dist})
                    fi
                done
            fi
            if [[ -f "${work_pfl}" ]]; then
                if [[ ${_force} == true ]]; then
                    mv "${work_pfl}" "${PROD_DIST_DIR}"
                else
                    if ! mv -n "${work_pfl}" "${PROD_DIST_DIR}"; then
                        echo -e "Could not move ${work_pfl} to ${PROD_DIST_DIR}" >&2
                        echo 1 >${status_log}
                        exit  # the subshell
                    fi
                fi
                pfl="${prod_pfl}"
            else
                if [[ -f ${prod_pfl} ]]; then
                    pfl="${prod_pfl}"
                fi
            fi

            distributions=(${prod_distributions[@]})
            links_dir=${PROD_DIST_DIR}
        fi

        echo "Matching distributions ${distributions[@]}"

        # Finally, install the distribution.
        if [[ ${#distributions[@]} -gt 0 ]]; then

            mkdir -p "${version_location}"

            prefix_location="${version_location}/prefix"
            site_packages_location="${prefix_location}/lib/${PYTHON_VERSION}/site-packages"
            # Check if there is Pipfile.lock to create the lightweight venv first.
            # This will fail if necessary dependencies aren't installed.
            if [[ -v pfl ]]; then
                echo "Installing venv from ${pfl}"
                cd ${version_location}
                cp "${pfl}" .
                if ! dls-py3 pipfilelock-to-venv "${pipfilelock}"; then
                    echo -e "\nCreating lightweight virtualenv failed." >&2
                    echo 1 >${status_log}
                    exit  # the subshell
                fi
            else
                echo "No Pipfile.lock is present"
            fi

            # Perform the actual installation using Pip.
            pip3 install --ignore-installed --no-index --no-deps \
                            --find-links=${links_dir} --prefix=${prefix_location} \
                            ${specifier}
            echo $? >${status_log}

            if [[ -d lightweight-venv ]]; then
                # Change header to use the lightweight-venv version of Python.
                shebang='#!'
                new_header="${shebang}${version_location}/lightweight-venv/bin/python"
                for script in ${prefix_location}/bin/* ; do
                    sed -i "1 s|^.*$|${new_header}|" "${script}"
                done
            fi
        else
            echo 1 >${status_log}
            echo "No matching distribution was found for ${specifier}" >$2
            exit  # the subshell
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
    echo "These warnings were generated by a python3lib build." >> ${error_log}
    echo "The exit status was 0 so the build itself succeeded." >> ${error_log}
    cat ${error_log} | mail -s "Warnings from successful build: ${_area} ${_module} ${_version}" $_email || SysLog err "Failed to email build errors"
fi

SysLog info "Build complete"
