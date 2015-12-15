#!/bin/env dls-python
# This script comes from the dls_scripts python module

import sys
import os
import shutil
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


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_technical_area_valid(args, parser)

    module = args.module_name

    source = path.devModule(module, args.area)
    logging.debug(source)
    release = path.prodModule(module, args.area)
    logging.debug(release)

    # Check for existence of this module in various places in the repository and note revisions
    if not vcs_git.is_repo_path(source):
        parser.error("Repository does not contain " + source)

    if vcs_git.is_repo_path(source):
        if os.path.isdir('./' + module):
            repo = vcs_git.git.Repo(module)
            last_trunk_rev = vcs_git.list_module_releases(git.Repo(repo))
        else:
            vcs_git.clone(source, module)
            repo = vcs_git.git.Repo(module)
            last_trunk_rev = vcs_git.list_module_releases(git.Repo(repo))
            shutil.rmtree(module)

    if vcs_git.is_repo_path(release):
        last_release_rev = "last rev"
        # svn.info2(release, recurse=False)[0][1]["last_changed_rev"].number
        last_release_num = "last num"
        # e.sortReleases([x["name"] for x in svn.ls(release)])[-1].split("/")[-1]
        # print the output
        if last_trunk_rev > last_release_rev:
            print(module + " (" + last_release_num + "): Outstanding changes. "
                                                     "Release = r" + str(last_release_rev) +
                                                     ",Trunk = r" + str(last_trunk_rev))
        else:
            print(module + " (" + last_release_num + "): Up to date.")
    else:
        print(module + " (No release done): Outstanding changes.")
    

if __name__ == "__main__":
    sys.exit(main())
