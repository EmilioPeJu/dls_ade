#!/bin/env dls-python
# This script comes from the dls_scripts python module

import sys
import shutil
import logging
from dls_ade.argument_parser import ArgParser
from dls_ade import path_functions as pathf
from dls_ade import vcs_git
from pkg_resources import require
require('GitPython')
import git

logging.basicConfig(level=logging.DEBUG)

usage = """
Default <area> is 'support'.
Check if a module in the <area> area of the repository has had changes committed since its last release.
"""


def make_parser():
    """
    Takes default parser arguments and adds module_name

    Returns:
        :class:`argparse.ArgumentParser`:  ArgParse instance
    """
    parser = ArgParser(usage)
    parser.add_module_name_arg()

    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()

    pathf.check_technical_area(args.area, args.module_name)

    module = args.module_name
    source = pathf.dev_module_path(module, args.area)
    logging.debug(source)

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
        raise Exception(source + " does not exist on the repository.")

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
