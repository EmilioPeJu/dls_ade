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
logging.basicConfig(filename='./list_releases.log', level=logging.DEBUG)


usage = """
Default <area> is 'support'.

List the releases of a module in the release area of <area>. By default uses
the epics release number from your environment to work out the area on disk to
look for the module, this can be overridden with the -e flag.
"""


def get_rhel_version():
    """

    :return:
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

    :return:
    """
    parser = ArgParser(usage)
    parser.add_argument(
        "module_name", type=str, default=None, help="name of module to release")
    parser.add_argument(
        "-l", "--latest", action="store_true", dest="latest",
        help="Only print the latest release")
    parser.add_argument(
        "-g", "--git", action="store_true", dest="git",
        help="Print releases available in git")
    parser.add_argument(
        "-e", "--epics_version", action="store", type=str, dest="epics_version",
        help="change the epics version, default is " + e.epicsVer() +
             " (from your environment)")
    parser.add_argument(
        "-r", "--rhel_version", action="store", type=int, dest="rhel_version",
        default=get_rhel_version(),
        help="change the rhel version of the " + "environment, default is " +
             get_rhel_version() + " (from your system)")

    return parser


def check_epics_version(args, parser):
    """

    :param args:
    :param parser:
    :return:
    """
    if args.epics_version:
        if not args.epics_version.startswith("R"):
            args.epics_version = "R{0}".format(args.epics_version)
        if e.epics_ver_re.match(args.epics_version):
            e.setEpics(args.epics_version)
        else:
            parser.error("Expected epics version like R3.14.8.2, got: " +
                         args.epics_version)


def check_technical_area(args, parser):
    """
    Checks if given area is IOC and if so, checks that the technical area is also provided.
    Raises parser error if not.
    :param args: Parser arguments
    :type args: ArgumentParser Namespace
    :param parser: Parser
    :type parser: ArgumentParser
    :return: Null
    """
    if args.area == "ioc" \
            and len(args.module_name.split('/')) < 2:
        parser.error("Missing Technical Area under Beamline")


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_epics_version(args, parser)
    check_technical_area(args, parser)

    module = args.module_name

    # >>> Not sure what this is for
    # Force options.svn if no releases in the file system
    if args.area in ["etc", "tools", "epics"]:
        args.git = True
    # >>>

    # Check for the existence of releases of this module/IOC    
    releases = []
    if args.git:
        # List branches of repository
        target = "the repository"
        source = os.path.join(pathf.prodArea(args.area), module)
        if vcs_git.is_repo_path(source):
            if os.path.isdir('./' + module):
                repo = vcs_git.git.Repo(module)
                releases = vcs_git.list_module_releases(repo)
            else:
                vcs_git.clone(source, module)
                repo = vcs_git.git.Repo(module)
                releases = vcs_git.list_module_releases(repo)
                shutil.rmtree(module)
    else:
        # List branches from prod
        target = "prod"
        prodArea = e.prodArea(args.area)
        if args.area == 'python' and args.rhel_version >= 6:
            prodArea = os.path.join(prodArea, "RHEL%s-%s" %
                                    (args.rhel_version, platform.machine()))
        release_dir = os.path.join(prodArea, module)

        if os.path.isdir(release_dir):
            for p in os.listdir(release_dir):
                if os.path.isdir(os.path.join(release_dir, p)):
                    releases.append(p)

    # check some releases have been made
    if len(releases) == 0:
        if args.git:
            msg = "No releases made in git"
        else:
            # >>> Prints "No releases made for None" if epics_version not set
            msg = "No releases made for %s" % args.epics_version
        print(module + ": " + msg)
        return 1

    # sort the releases
    releases = e.sortReleases(releases)

    if args.latest:
        print("The latest release for " + module + " in " + target +
              " is: " + releases[-1])
    else:
        print("Previous releases for " + module + " in " + target + ":")
        for path in releases:
            print(path)

if __name__ == "__main__":
    sys.exit(main())
