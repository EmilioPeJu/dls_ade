#!/bin/env dls-python
# This script comes from the dls_scripts python module


import os
import sys
import logging
from argument_parser import ArgParser
from dls_environment import environment
import path_functions as path
import vcs_git
from pkg_resources import require
require('GitPython')
import git

e = environment()
logging.basicConfig(level=logging.DEBUG)

BLUE = 34
GREEN = 32
CYAN = 36

usage = """
Default <area> is 'support'.
Check if a module in the <area> area of the repository has had changes committed since its last release.
"""


def make_parser():

    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, help="name of module to release")
    return parser


def check_technical_area_valid(args, parser):

    if args.area == "ioc" and not len(args.module.split('/')) > 1:
        parser.error("Missing Technical Area Under Beamline")


def colour(word, col):
    # >>> I have just hard coded the char conversion of %27c in, as I couldn't find the
    # .format equivalent of %c, is anything wrong with this?
    return '\x1b[{col}m{word}\x1b[0m'.format(col=col, word=word)



def main():

    parser = make_parser()
    args = parser.parse_args()

    check_technical_area_valid(args, parser)

    module = args.module_name

    source = path.devModule(module, args.area)
    logging.debug(source)

    logging.debug("Got to 1")

    # Check for existence of this module in various places in the repository and note revisions
    if not vcs_git.is_repo_path(source):
        parser.error("Repository does not contain " + source)

    logging.debug("Got to 2")

    if vcs_git.is_repo_path(source):
        if os.path.isdir('./' + module):
            logging.debug("Got to 3a")
            repo = vcs_git.git.Repo(module)
            releases = vcs_git.list_module_releases(repo)
        else:
            logging.debug("Got to 3b")
            vcs_git.clone(source, module)
            repo = vcs_git.git.Repo(module)
            releases = vcs_git.list_module_releases(repo)

        last_release_num = releases[-1]
        logging.debug(last_release_num)
    else:
        parser.error(source + "does not exist on the repository.")

    # if hasn't been released:
    # print(module + " (No release done): Outstanding changes.")

    logging.debug("Got to 4")

    logs = repo.git.log(last_release_num + "..HEAD", "--format=%h %aD %cn %n %s %n %b %n%n%n%n").split('\n\n\n\n\n')

    if logs:
        print("Changes have been made to " + module + " since release " + last_release_num)
        formatted_logs = []
        for entry in logs:
            commit = entry.split(' ')[0]

            if len(entry.split(' ')[2]) == 1:
                date = '0' + entry.split(' ')[2] + ' ' + entry.split(' ')[3] + ' ' + entry.split(' ')[4]
            else:
                date = entry.split(' ')[2] + ' ' + entry.split(' ')[3] + ' ' + entry.split(' ')[4]

            name = '{:<20}'.format(entry.split(' ')[7] + ' ' + entry.split(' ')[8])

            if len(entry.split('\n')) > 3:
                message = entry.split('\n')[1] + ' - ' + entry.split('\n')[2]
            else:
                message = entry.split('\n')[1]

            formatted_logs.append(colour(commit, BLUE) + ' ' + colour(date, CYAN) + ' ' +
                              colour(name, GREEN) + ': ' + message)
            for log in formatted_logs:
                print(log)
    else:
        print("No changes made to " + module + " since release " + last_release_num)

    # >>> More concise log messages for changes. Make check for no release.

if __name__ == "__main__":
    sys.exit(main())
