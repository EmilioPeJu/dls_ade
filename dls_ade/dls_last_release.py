#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
Last release
"""

import os
import time
import sys
import logging
import csv
import argparse
import requests

from dls_ade.constants import GELFLOG_SERVER
from dls_ade import logconfig

USER = os.getenv("USER")
# Read-only API token for Graylog - see GRAYLOG_TOKEN.md
TOKEN = "1pqc889ahskd3t6mfgm00rhm451hduo5je9kvlg8c1n61i4i23s3"
LJUST = 12

JOB_NAME = "Job name"
STATUS_STR = "Job status"
LOG_FILE = "Log file"
ERR_FILE = "Err msgs"

LOG_FILE_MSG = "Build log: "
ERR_FILE_MSG = "errors: "

LOCAL = "Local"
BUILD = "Build"
FIND_BUILD_STR = {LOCAL: '"Local test-build parameters"',
                  BUILD: '"Build server job parameters"'}
#Tools and etc have different messages at start of build
STARTED_STR = "Starting build"
FINISHED_STR = ("Build complete", "Build job failed")

WINDOWS_WARNING = "Cannot retrieve build status for windows builds"

#TODO:
'''
windows builds ---> At the moment they will get stuck in "Queueing" because the windows
                    build script does not currently log to graylog. Checks whether builds
                    are windows and displays a warning message
'''

usage = """
This script will list the latest build(s) from a specific user or from any user.
The script gives the location of the error file, the log file, the build name and the status of the build.
"""

def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Flags:

        * -w (wait)
        * -u (user)
        * -e (errors)
        * -n (nresults)
        * -l (local)
        * -t (time)

    Returns:
        :class:`argparse.ArgumentParser`:  ArgParse instance
    """
    parser = argparse.ArgumentParser(
        description=usage,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-w", "--wait", action="store_true",
        help="If set, wait for the most recent build to finish")
    parser.add_argument(
        "-u", "--user", action="store", type=str,
        default=USER,
        help="User (default is $USER). Use FED ID or 'all' to see builds for all users")
    parser.add_argument(
        "-e", "--errors", action="store_true",
        help="If set, print build errors")
    parser.add_argument(
        "-n", "--nresults", action="store", type=int,
        default=1,
        help="Number of results to display (default is 1)")
    parser.add_argument(
        "-l", "--local", action="store_true",
        default=False,
        help="Include local builds")
    parser.add_argument(
        "-t", "--time_frame", action="store", type=int,
        default=2,
        help="Graylog search period in hours. Default is 2 hours.")

    return parser


def create_graylog_query(query_str, time_frame):
    """Create the parameters

    Args:
        query_str(str): The Graylog query string (lucene syntax)

    Returns:
        dict: Params for requests.get() from graylog API
    """
    query_params = {
        "query": query_str,
        "range": str(time_frame*60*60),
        "fields":"message, build_name",
        "limit": 800
    }
    return query_params


def graylog_request(params):
    """Make a graylog request

    Args:
        params(dict): Params dict returned from create_graylog_query (or other create
                      function)

    Returns:
        reponse object: Graylog response
    """
    url = "https://" + GELFLOG_SERVER + "/api/search/universal/relative"
    auth = (TOKEN, "token")
    r = requests.get(url, auth=auth, params=params)
    return r


def parse_graylog_response(graylog_response):
    """Parse the graylog response as a list of dictionaries in reverse
    time order

    Args:
        graylog_response(response object): Response returned by graylog_request()

    Returns:
        list of dict: Graylog search results as a list of dictionaries
        sorted in reverse time order.
    """
    reader = csv.reader(graylog_response.iter_lines(), delimiter=',')
    try:
        header = reader.next()
    except StopIteration:
        pass

    dicts = []
    for row in reader:
        dictline = {}
        for h, hline in enumerate(header):
            dictline[hline] = row[h]
        dicts.append(dictline)
    dicts = sorted(dicts, key=lambda i: i["timestamp"], reverse=True)
    return dicts


def get_graylog_response(params):
    """Send request to graylog API and parse the result as list of dicts

    Args:
        params(dict): Params dict returned from create_graylog_query (or other create
                      function)

    Returns:
        list of dict: Graylog search results as a list of dictionaries
        sorted in reverse time order.
    """
    res = graylog_request(params)
    return parse_graylog_response(res)


def create_build_job_query(user, time_frame, local=False):
    """Create the query to get build jobs from graylog

    Args:
        user(str): Fed ID
        time_frame(int): Graylog search period in hours
        local(bool): If True also search string for local builds

    Returns:
        str: Query string for a graylog request to get build jobs
    """
    query_str = 'application:dls-release.py AND (message:'
    if local:
        query_str += FIND_BUILD_STR[BUILD] + ' OR message:' \
                  + FIND_BUILD_STR[LOCAL] + ")"
    else:
        query_str += FIND_BUILD_STR[BUILD] + ")"
    if user != "all":
        query_str += " AND username:" + user
    return create_graylog_query(query_str, time_frame)


def create_windows_query(build_job, time_frame):
    query_str = 'message:"Build request file: ' + build_job + '"'
    return create_graylog_query(query_str, time_frame)


def create_build_validity_query(build_job, time_frame):
    query_str = 'message:"\'build_name\': \'' + build_job + '\',"'
    return create_graylog_query(query_str, time_frame)


def create_build_status_query(build_job, time_frame):
    query_str = 'application_name:dcs_build_job* AND build_name:"' + build_job + '"'
    return create_graylog_query(query_str, time_frame)


def create_build_started_query(build_job, time_frame):
    query_str = ('application_name:dcs_build_job* AND build_name:"' +
                 build_job + '"' + ' AND message:"Starting build"')
    return create_graylog_query(query_str, time_frame)


def create_build_finished_query(build_job, time_frame):
    query_str = ('application_name:dcs_build_job* AND build_name:"' +
                 build_job + '" ' +
                 'AND (message:"Build complete" OR message:"Build job failed")')
    return create_graylog_query(query_str, time_frame)


def extract_build_jobs(response_dict_list, time_frame, njobs=1):
    """Produce a list of build names from a graylog response

    Args:
        response_dict_list(list of dicts): The response from a graylog query
                                           using the create_build_job_query query str
        time_frame(int): Graylog search period in hours
        njobs(int): Number of build jobs to extract. Defaults to 1

    Returns:
        list of str: List of build names
    """
    build_jobs = []
    if njobs > len(response_dict_list):
        logging.getLogger("usermessages").info(str(len(response_dict_list)) +
                                               " build jobs in last " +
                                               str(time_frame) +
                                               " hours. Use -t to specify search range")
        njobs = len(response_dict_list)
    for i in range(njobs):
        build_job = response_dict_list[i]["message"].split("build_name': '")[1].split("',")[0]
        build_jobs.append(build_job)
    return build_jobs


def get_build_jobs(time_frame, user=USER, njobs=1, local=False):
    """Get a list of latest njobs builds for a specific user or all users

    Args:
        time_frame(int): Graylog search period in hours
        user(str): Fed ID or "all"
        njobs(int): Number of results
        local(bool): If True also search string for local builds

    Returns:
        list of str: List of build names
    """
    graylog_dicts_list = get_graylog_response(create_build_job_query(user, time_frame, local))
    build_jobs = extract_build_jobs(graylog_dicts_list, time_frame, njobs=njobs)
    return build_jobs


def parse_timestamp(timestamp):
    [date, rest] = timestamp.split("T")
    [time, rest] = rest.split(".")
    return time + " " + date


def print_err_file(err_file):
    with open(err_file) as f:
        for line in f:
            logging.getLogger("output").info(line)


def display_build_job_info(status_dict):
    job_info = ""
    for key in [LOG_FILE, ERR_FILE, JOB_NAME, STATUS_STR]:
        if key in status_dict:
            job_info += "{:<{}s}: {}\n".format(key, LJUST, status_dict[key])
    logging.getLogger("output").info(job_info)


def is_windows(build_job, time_frame):
    """Check if windows build

    Args:
        build_job(str): Build job name
        time_frame(int): Graylog search period in hours

    Returns:
        bool: True if windows build
    """
    if build_job.startswith("local") or "_etc_" in build_job or "_tools_" in build_job:
        windows = False
    else:
        graylog_dicts_list = get_graylog_response(create_windows_query(build_job, time_frame))
        try:
            windows = ".windows" in graylog_dicts_list[0]["message"]
        except IndexError:
            logging.getLogger("usermessages").error("Cannot determine linux/windows build for " +
                                                    build_job)
            sys.exit(1)
    return windows


def get_completed_dict(build_job, time_frame):
    """Return job completion dict if job has completed

    Args:
        build_job(str): Build job name
        time_frame(int): Graylog search period in hours

    Returns:
        response_dict(dicts): The response from a graylog query using the
                              create_build_finished_query query str.
                              None if build job not complete.
    """
    finished_dicts_list = get_graylog_response(create_build_finished_query(build_job, time_frame))
    if len(finished_dicts_list) == 1:
        return finished_dicts_list[0]


def get_started_dict(build_job, time_frame):
    """Return job started dict if job has started

    Args:
        build_job(str): Build job name
        time_frame(int): Graylog search period in hours

    Returns:
        response_dict(dicts): The response from a graylog query using the
                              create_started_finished_query query str.
                              None if build job not started.
    """
    started_dicts_list = get_graylog_response(create_build_started_query(build_job, time_frame))
    if len(started_dicts_list) == 1:
        return started_dicts_list[0]


def find_file(started_dict, ext):
    """Extract log or err file path from response dict list

    Args:
        started_dict(dict): Graylog response dict from get_started_dict
        ext (str): File extension. Should be "log" or "err"

    Returns:
        str: Log or Err file location
    """
    start_message = started_dict["message"]
    try:
        if ext == "log":
            filepath = start_message.split(LOG_FILE_MSG)[1].split(".log")[0] + ".log"
        elif ext == "err":
            filepath = start_message.split(ERR_FILE_MSG)[1].split(".err")[0] + ".err"
    except IndexError:
        filepath = "No " + ext + " file available"
    return filepath


def get_completed_status(completed_dict):
    """Determine whether build job completed successfully

    Args:
        completed_dict(dict): Graylog response dict from get_completed_dict

    Returns:
        str: Status of build job
    """
    complete_message = completed_dict["message"]
    complete_timestamp = completed_dict["timestamp"]
    status = [s for s in FINISHED_STR if complete_message.startswith(s)][0]
    return status + " at " + parse_timestamp(complete_timestamp)


def get_build_status(build_job, time_frame):
    """Find the status of a build job. The status of the build job, location or the
       log and err files in a dictionary.

    Args:
        build_job(str): build job name
        time_frame(int): Graylog search period in hours

    Returns:
        dict: Dictionary with build name, log file, err file and build status
    """
    status = "Queueing"
    status_dict = {JOB_NAME: build_job}

    started = get_started_dict(build_job, time_frame)
    if started is not None:
        status_dict[LOG_FILE] = find_file(started, "log")
        status_dict[ERR_FILE] = find_file(started, "err")

    completed = get_completed_dict(build_job, time_frame)
    if completed is not None:
        status = get_completed_status(completed)

    if started and not completed:
        status = "Running"

    status_dict[STATUS_STR] = status
    return status_dict


def _main():

    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger(name="usermessages")
    output = logging.getLogger(name="output")

    parser = make_parser()
    args = parser.parse_args()

    build_jobs = get_build_jobs(
        time_frame=args.time_frame, user=args.user, njobs=args.nresults, local=args.local)

    for job in build_jobs:
        waiting = False
        windows = is_windows(job, args.time_frame)

        if windows:
            usermsg.info("\r{:<{}s}: {}".format("Warning", LJUST, WINDOWS_WARNING))

        if args.wait and not windows:
            while get_completed_dict(job, args.time_frame) is None:
                waiting = True
                sys.stdout.write(
                    "Waiting for {}: {}\r".format(job,
                                                  time.ctime()))
                sys.stdout.flush()
                #output.info(time.ctime(), end="\r", flush=True)#python 3 equivalent
                time.sleep(1)

        if waiting:
            output.info("\rCompleted job: {}: {}\n".format(job, time.ctime()))

        status_dict = get_build_status(job, args.time_frame)
        display_build_job_info(status_dict)

        if args.errors and ERR_FILE in status_dict and os.path.isfile(status_dict[ERR_FILE]):
            print_err_file(status_dict[ERR_FILE])


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-last-release.py')
        _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception(
            "ABORT: Unhandled exception (see trace below): {}".format(e)
        )
        exit(1)

if __name__ == "__main__":
    main()
