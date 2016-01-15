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

e = environment()
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
    parser.add_argument(
        "module_name", type=str, default=None, help="Name of module to list releases for")
    parser.add_argument(
        "-l", "--latest", action="store_true", dest="latest",
        help="Only print the latest release")
    parser.add_argument(
        "-g", "--git", action="store_true", dest="git",
        help="Print releases available in git")
    parser.add_argument(
        "-e", "--epics_version", action="store", type=str, dest="epics_version",
        help="Change the epics version, default is " + e.epicsVer() +
             " (from your environment)")
    parser.add_argument(
        "-r", "--rhel_version", action="store", type=int, dest="rhel_version",
        default=get_rhel_version(),
        help="Change the rhel version of the environment, default is " +
             get_rhel_version() + " (from your system)")

    return parser


def check_epics_version(epics_version):
    """
    Checks if epics version is provided. If it is, checks that it starts with 'R' and if not appends an 'R'.
    Then checks if the epics version matches the reg ex. Then sets environment epics version.

    Args:
        epics_version: Epics version to check

    Raises:
        Expected epics version like R3.14.8.2, got: <epics_version>
    """
    if epics_version:
        if not epics_version.startswith("R"):
            epics_version = "R{0}".format(epics_version)
        if e.epics_ver_re.match(epics_version):
            e.setEpics(epics_version)
        else:
            raise Exception("Expected epics version like R3.14.8.2, got: " + epics_version)


def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that the technical area is also provided.

    Args:
        area: Area of repository
        module: Module to check

    Raises:
        "Missing Technical Area under Beamline"
    """

    if area == "ioc" \
            and len(module.split('/')) < 2:
        raise Exception("Missing Technical Area under Beamline")


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_epics_version(args.epics_version)
    check_technical_area(args.area, args.module_name)

    # >>> Not sure what this is for
    # # Force options.svn if no releases in the file system
    # if args.area in ["etc", "tools", "epics"]:
    #     args.git = True

    # Check for the existence of releases of this module/IOC    
    releases = []
    if args.git:
        # List branches of repository
        target = "the repository"
        source = pathf.devModule(args.module_name, args.area)

        repo = vcs_git.temp_clone(source)
        releases = vcs_git.list_module_releases(repo)
        shutil.rmtree(repo.working_tree_dir)

    else:
        # List branches from prod
        target = "prod"
        prodArea = e.prodArea(args.area)
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

    releases = e.sortReleases(releases)

    if args.latest:
        print("The latest release for " + args.module_name + " in " + target +
              " is: " + releases[-1])
    else:
        print("Previous releases for " + args.module_name + " in " + target + ":")
        for release in releases:
            print(release)

if __name__ == "__main__":
    sys.exit(main())
