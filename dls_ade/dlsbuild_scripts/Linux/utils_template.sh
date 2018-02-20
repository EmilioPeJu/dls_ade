#!/usr/bin/env bash

# Arguments: 
#     1) log level. Valid levels are: alert, crit, debug, emerg, err, info, notice, warning
#     2) Message
SysLog()
{
    echo ${@:2} |
    /dls_sw/prod/tools/RHEL6-x86_64/util-linux/2-30-1/prefix/bin/logger \
    --tag dcs_build_server-$(uname -m) \
    -s -d -p local2.$1 \
    -n cs03r-sc-serv-30 -P 5150 \
    --rfc5424 \
    --sd-id dcs@32121 \
      --sd-param build_job_parameters=\"build_name=$_build_name\ area=$_area\ module=$_module\ version=$_version\ email=$_email\ username=$_user\" \
    || echo "Build server error. logger failed:" $_build_name
}

ReportFailure()
{
    { [ -f "$1" ] && cat $1 || echo $*; } |
    mail -s "Build Errors: $_area $_module $_version" $_email || echo "Build server error. mail failed:" $_build_name
    SysLog err "Build job failed: " $*
    exit 2
}

