#!/bin/env dls-python
# This script comes from the dls_scripts python module
import os
import sys
import shutil
import platform
from dls_environment import environment
import logging
from argument_parser import ArgParser
import path_functions as pathf
import vcs_git

env = environment()
logging.basicConfig(level=logging.DEBUG)


usage = """
Default <area> is 'support'.

List the releases of a module in the release area of <area>. By default uses
the epics release number from your environment to work out the area on disk to
look for the module, this can be overridden with the -e flag.
"""


def get_rhel_version():
    """
    Checks if platform is Linux redhat, if so returns base version number from environment (e.g. returns 6 if 6.7),
    if not returns default of 6
    
    Returns:
        Rhel version number
    """
    default_rhel_version = "6"
    if platform.system() == 'Linux' and platform.dist()[0] == 'redhat':
        dist, release_str, name = platform.dist()
        release = release_str.split(".")[0]
        return release
    else:
        return default_rhel_version


def make_parser():
    """
    Takes default parser and adds 'module_name' and 'latest', 'git', 'epics_version' & 'rhel_version'

    Returns:
        ArgumentParser instance
    """
    parser = ArgParser(usage)
    parser.add_module_name_arg()
    parser.add_epics_version_flag()
    parser.add_git_flag(
        help_msg="Print releases available in git")

    parser.add_argument(
        "-l", "--latest", action="store_true", dest="latest",
        help="Only print the latest release")
    parser.add_argument(
        "-r", "--rhel_version", action="store", type=int, dest="rhel_version",
        default=get_rhel_version(),
        help="Change the rhel version of the environment, default is " +
             get_rhel_version() + " (from your system)")

    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()

    env.check_epics_version(args.epics_version)
    pathf.check_technical_area(args.area, args.module_name)

    # >>> Not sure what this is for
    # # Force options.svn if no releases in the file system
    # if args.area in ["etc", "tools", "epics"]:
    #     args.git = True

    # Check for the existence of releases of this module/IOC    
    releases = []
    if args.git:
        # List branches of repository
        target = "the repository"
        source = pathf.dev_module_path(args.module_name, args.area)

        repo = vcs_git.temp_clone(source)
        releases = vcs_git.list_module_releases(repo)
        shutil.rmtree(repo.working_tree_dir)

    else:
        # List branches from prod
        target = "prod"
        prodArea = env.prodArea(args.area)
        if args.area == 'python' and args.rhel_version >= 6:
            prodArea = os.path.join(prodArea, "RHEL{0}-{1}".format(args.rhel_version,
                                                                   platform.machine()))
            logging.debug(prodArea)
        release_dir = os.path.join(prodArea, args.module_name)

        if os.path.isdir(release_dir):
            for p in os.listdir(release_dir):
                if os.path.isdir(os.path.join(release_dir, p)):
                    releases.append(p)

    # Check some releases have been made
    if len(releases) == 0:
        if args.git:
            print(args.module_name + ": No releases made in git")
        else:
            print(args.module_name + ": No releases made for " + args.epics_version)
        return 1

    releases = env.sortReleases(releases)

    if args.latest:
        print("The latest release for " + args.module_name + " in " + target +
              " is: " + releases[-1])
    else:
        print("Previous releases for " + args.module_name + " in " + target + ":")
        for release in releases:
            print(release)

if __name__ == "__main__":
    sys.exit(main())
