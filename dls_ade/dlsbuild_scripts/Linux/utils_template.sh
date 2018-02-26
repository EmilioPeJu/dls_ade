#!/usr/bin/env bash

# Arguments: 
#     1) log level. Valid levels are: alert, crit, debug, emerg, err, info, notice, warning
#     2) Message
SysLog()
{
    local dls_syslog_server=cs03r-sc-serv-30
    local dls_syslog_server_port=5150

    local syslog_level_str=$1
    local syslog_message=${@:2}

    # Convert the log level string (arg 1) into syslog RFC5424 PRI field integer,
    # assuming log facility 'local2'.
    case "${syslog_level_str}" in
    alert)
      PRI=146
      ;;
    crit|err*)
      PRI=147
      ;;
    warn*)
      PRI=148
      ;;
    notice)
      PRI=149
      ;;
    info)
      PRI=150
      ;;
    debug)
      PRI=151
      ;;
    *)
      PRI=150
      ;;
    esac

    # Send the log message somewhere.
    # Fail safe implmented so that different logging mechanisms are tried in order, catching failures:
    #    1: dls-logger (requires module controls-tools to be pre-loaded)
    #    2: netcat (nc)
    #    3:
    echo ${syslog_message} |
    dls-logger \
    --tag dcs_build_job-$(uname -m) \
    -s -d -p local2.$1 \
    -n ${dls_syslog_server} -P ${dls_syslog_server_port} \
    --rfc5424 \
    --sd-id dcs@32121 \
      --sd-param build_job_parameters=\"build_name=$_build_name\ area=$_area\ module=$_module\ version=$_version\ email=$_email\ username=$_user\" \
    || echo "<${PRI}>$(date --rfc-3339=ns | sed 's/ /T/; s/\(\....\).*-/\1-/g') $(hostname) ${0##*/}($$) - - [dcs@32121 build_job_parameters=\"build_name=$_build_name area=$_area module=$_module version=$_version email=$_email username=$_user\"] ${syslog_message}" |
    nc -w1 -u ${dls_syslog_server} ${dls_syslog_server_port} \
    || echo ${syslog_message} |
    logger \
    -t "<${PRI}>$(date --rfc-3339=ns | sed 's/ /T/; s/\(\....\).*-/\1-/g') $(hostname) ${0##*/}($$) - - [dcs@32121 build_job_parameters=\"build_name=$_build_name area=$_area module=$_module version=$_version email=$_email username=$_user\"] " \
    -s -d -p local2.$1 \
    || echo "(logger failed) Build server error:" $_build_name ${syslog_message}
}

ReportFailure()
{
    { [ -f "$1" ] && cat $1 || echo $*; } |
    mail -s "Build Errors: $_area $_module $_version" $_email || echo "Build server error. mail failed:" $_build_name
    SysLog err "Build job failed: " $*
    exit 2
}

