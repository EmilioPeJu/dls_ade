#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
Last release
"""

import os
import re
import time
import sys
import shutil
import json
import platform
import logging
import requests
import csv
import ast
import argparse

from dls_ade.dls_environment import environment
from dls_ade.argument_parser import ArgParser
from dls_ade.dls_utilities import check_technical_area
from dls_ade import vcs_git, Server
from dls_ade.constants import GELFLOG_SERVER
from dls_ade import logconfig

USER = os.getenv("USER")
TOKEN = "582e10ggh6gi8fb28of7d9f33v9mc2oda7fepl2eqmvvg3ta1g6"
LJUST = 12

JOB_NAME = "Job name"
STATUS_STR = "Job status"
LOG_FILE = "Log file"
ERR_FILE = "Err msgs"

LOCAL = "Local"
BUILD = "Build"
FIND_BUILD_STR = {LOCAL: '"Local test-build parameters"',
                  BUILD: '"Build server job parameters"'}
#Tools and etc have different messages at start of build
STARTED_STR = ("Starting build", "Building tool", "Building etc")
FINISHED_STR = ("Build complete", "Build job failed")

#TODO:
'''
windows builds ---> At the moment they will get stuch in "Queueing" because the windows
                    build script does not currently log to graylog
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
        * -b (build)

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

    # The following arguments cannot be used together
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-l", "--local-only", action="store_true",
        default=False, help="If set, only local builds will be shown")
    group.add_argument(
        "-b", "--build-only", action="store_true",
        default=False, help="If set, only build server builds will be shown")
    return parser


def create_graylog_query(query_str):
    """Create the parameters

    Args:
        query_str(str): The Graylog query string (lucene syntax)

    Returns:
        dict: Params for requests.get() from graylog API
    """
    query_params = {
        "query": query_str,
        "range": str(3*24*60*60),
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
    auth = (TOKEN,"token")
    r = requests.get(url, auth=auth,params=params)
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
        for h in range(len(header)):
            dictline[header[h]] = row[h]
        dicts.append(dictline);
    dicts = sorted(dicts, key = lambda i: i["timestamp"], reverse=True)
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


def create_build_job_query(user, local_only=False, build_only=False):
    """Create the query to get build jobs from graylog

    Args:
        user(str): Fed ID
        local_only(bool): If True search string for local builds only
        build_only(bool): If True search string for non-local builds only

    Returns:
        str: Query string for a graylog request to get build jobs
    """
    query_str = 'application:dls-release.py AND (message:'
    if local_only:
        query_str += FIND_BUILD_STR[LOCAL] + ")"
    elif build_only:
        query_str += FIND_BUILD_STR[BUILD] + ")"
    else:
        query_str += FIND_BUILD_STR[BUILD] + ' OR message:' \
                  + FIND_BUILD_STR[LOCAL] + ")"
    if user != "all":
        query_str += " AND username:" + user
    return create_graylog_query(query_str)


def create_build_validity_query(build_job):
    query_str = 'message:"\'build_name\': \'' + build_job + '\',"'
    return create_graylog_query(query_str)


def create_build_status_query(build_job):
    query_str = 'application_name:dcs_build_job* AND build_name:"' + build_job + '"'
    return create_graylog_query(query_str)


def extract_build_jobs(response_dict_list, n=1):
    """Produce a list of build names from a graylog response

    Args:
        response_dict_list(list of dicts): The response from a graylog query
                                           using the create_build_job_query query str

    Returns:
        list of str: List of build names
    """
    build_jobs = []
    if n > len(response_dict_list):
        print(str(len(response_dict_list)) + " build jobs in time period")
        n = len(response_dict_list)
    for i in range(n):
        build_name = response_dict_list[i]["message"].split("build_name': '")[1].split("',")[0]
        build_jobs.append(build_name)
    return build_jobs
     

def get_build_jobs(user=USER, n=1, local_only=False, build_only=False):
    """Get a list of latest n builds for a specific user or all users 

    Args:
        user(str): Fed ID or "all"
        n(int): Number of results
        local_only(bool): If True search string for local builds only
        build_only(bool): If True search string for non-local builds only

    Returns:
        list of str: List of build names
    """
    graylog_dicts_list = get_graylog_response(create_build_job_query(user, local_only, build_only))
    build_jobs = extract_build_jobs(graylog_dicts_list, n=n)
    return build_jobs


def get_build_status(build_job):
    """Find the status of a build job. The status of the build job, location or the
       log and err files in a dictionary.

    Args:
        user(str): Fed ID or "all"
        n(int): Number of results
        local_only(bool): If True search string for local builds only
        build_only(bool): If True search string for non-local builds only

    Returns:
        dict: Dictionary with build name, log file, err file and build status
    """
    graylog_dicts_list = get_graylog_response(create_build_status_query(build_job))
    status_dict = build_status(build_job, graylog_dicts_list)
    return status_dict


def get_message_list(response_dict_list):
    return list(map(lambda x : x["message"], response_dict_list))


def get_timestamp_list(response_dict_list):
    return list(map(lambda x : x["timestamp"], response_dict_list))


def parse_timestamp(timestamp):
    [date, rest] = timestamp.split("T")
    [time, rest] = rest.split(".")
    return time + " " + date

  
def print_err_file(err_file):
    with open(err_file) as f:
        for line in f:
            print(line)


def display_build_job_info(status_dict):
    for key, value in status_dict.iteritems():
        print("\r{:<{}s}: {}".format(key, LJUST , value))
    print("")


def is_valid_build_job(build_job):
    """Check validity of build job name

    Args:
        build_job(str): Build job name

    Returns:
        bool: True if valid build job name
    """
    graylog_dicts_list = get_graylog_response(create_build_validity_query(build_job))
    return len(graylog_dicts_list) > 0


def is_build_complete(build_job):
    """Check whether build job has either completed successfully
       or failed

    Args:
        build_job(str): Build job name

    Returns:
        bool: True if build job has completed or failed
    """
    graylog_dicts_list = get_graylog_response(create_build_status_query(build_job))
    return is_finished(graylog_dicts_list)


def is_finished(response_dict_list):
    message_list = get_message_list(response_dict_list)
    return any(m.startswith(FINISHED_STR) for m in message_list)


def is_started(response_dict_list):
    message_list = get_message_list(response_dict_list)
    return any(m.startswith(STARTED_STR) for m in message_list)


def find_err_file(response_dict_list):
    """Extract error file path from response dict list

    Args:
        response_dict_list(list of str): Graylog response dict list after getting a graylog
                                         response with a create_build_status_query query str

    Returns:
        str: Err file location
    """
    message_list = get_message_list(response_dict_list)
    start_message = list(filter(lambda m: m.startswith(STARTED_STR), message_list))[0]
    try:
        err_file = start_message.split("errors: " )[1].split(".err")[0] + ".err"
    except IndexError:
        err_file = "No err file available"
    return err_file


def find_log_file(response_dict_list):
    """Extract log file path from response dict list

    Args:
        response_dict_list(list of str): Graylog response dict list after getting a graylog
                                         response with a create_build_status_query query str

    Returns:
        str: Log file location
    """
    message_list = get_message_list(response_dict_list)
    start_message = list(filter(lambda m: m.startswith(STARTED_STR), message_list))[0]
    try:
        log_file = start_message.split("Build log: " )[1].split(".log")[0] + ".log"
    except IndexError:
        log_file = "No log file available"
    return log_file


def get_complete_status(response_dict_list):
    """Determine whether build job completed successfully

    Args:
        response_dict_list(list of str): Graylog response dict list after getting a graylog
                                         response with a create_build_status_query query str

    Returns:
        str: Status of build job
    """
    message_list = get_message_list(response_dict_list)
    index = [message_list.index(m) for m in message_list if m.startswith(FINISHED_STR)][0]
    complete_message = message_list[index]
    complete_timestamp = get_timestamp_list(response_dict_list)[index]
    status = [s for s in FINISHED_STR if complete_message.startswith(s)][0]
    return status + " at " + parse_timestamp(complete_timestamp)


def build_status(build_name, response_dict_list):
    """Fill in the fields of a status dictionary using result of a graylog request

    Args:
        build_name(str): build name
        response_dict_list(list of str): Graylog response dict list after getting a graylog
                                         response with a create_build_status_query query str

    Returns:
        dict: Dictionary with build name, log file, err file and build status
    """
    status = "Queueing"
    status_dict = {JOB_NAME: build_name}
    #if len(response_dict_list) == 0 and is_valid_build_job(build_name):
    if len(response_dict_list) == 0:
        status_dict[STATUS_STR] = status
        return status_dict      

    complete = is_finished(response_dict_list)
    started = is_started(response_dict_list)

    if started:
        status_dict[LOG_FILE] = find_log_file(response_dict_list)
        status_dict[ERR_FILE] = find_err_file(response_dict_list)

    if complete:
        status = get_complete_status(response_dict_list)

    if started and not complete:
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
        user=args.user, n=args.nresults, local_only=args.local_only,
        build_only=args.build_only)
    for i in range(len(build_jobs)):
        waiting = False
        
        if args.wait:
            while not is_build_complete(build_jobs[i]):
                waiting = True
                sys.stdout.write(
                  "Waiting for {}: {}\r".format(build_jobs[i],
                                                time.ctime()))
                sys.stdout.flush()
                #print(time.ctime(), end="\r", flush=True)#python 3 equivalent
                time.sleep(1)

        if waiting:
            print("\rCompleted job: {}: {}\n".format(build_jobs[i],
                                                     time.ctime()))

        status_dict = get_build_status(build_jobs[i])
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
