#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
Check if a module on the repository has had changes committed to it since the last release was made.
"""

import sys
import shutil
import logging
from argument_parser import ArgParser
import path_functions as pathf
import vcs_git
from pkg_resources import require
require('GitPython')
import git

logging.basicConfig(level=logging.DEBUG)

usage = """
Default <area> is 'support'.
Check if <module_name> in the <area> area of the repository has had changes committed since its last release.
"""


def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Positional Arguments:
        * module_name

    Returns:
        An ArgumentParser instance
    """

    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, help="name of module to release")
    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()

    pathf.check_technical_area_valid(args.area, args.module_name)

    module = args.module_name
    source = pathf.dev_module_path(module, args.area)
    logging.debug(source)

    # Check for existence of this module in various places in the repository and note revisions
    if not vcs_git.is_server_repo(source):
        raise Exception("Repository does not contain " + source)

    if vcs_git.is_server_repo(source):
        repo = vcs_git.temp_clone(source)
        releases = vcs_git.list_module_releases(repo)

        if releases:
            last_release_num = releases[-1]
        else:
            print("No release has been done for " + module)
            # return so last_release_num can't be referenced before assignment
            return 1
    else:
        raise Exception(source + "does not exist on the repository.")

    # Get a single log between last release and HEAD
    # If there is one, then changes have been made
    logs = list(repo.iter_commits(last_release_num + "..HEAD", max_count=1))
    if logs:
        print("Changes have been made to " + module + " since release " + last_release_num)
    else:
        print("No changes have been made to " + module + " since most recent release " + last_release_num)

    shutil.rmtree(repo.working_tree_dir)


if __name__ == "__main__":
    sys.exit(main())
