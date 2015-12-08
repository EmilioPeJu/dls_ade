#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
import platform
# from dls_environment import environment
from argument_parser import ArgParser
import path_functions as path
import vcs_git

usage = """Default <area> is 'support'.
List the releases of a module in the release area of <area>. By default uses
the epics release number from your environment to work out the area on disk to
look for the module, this can be overridden with the -e flag.
"""


def get_rhel_version():
    default_rhel_version = "6"
    if platform.system() == 'Linux' and platform.dist()[0] == 'redhat':
        dist, release_str, name = platform.dist()
        release = release_str.split(".")[0]
        return release
    else:
        return default_rhel_version


def make_parser():

    # e = environment()

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
        help="change the epics version, default is " + "e.epicsVer()" +
             " (from your environment)")
    parser.add_argument(
        "-r", "--rhel_version", action="store", type=int, dest="rhel_version",
        default=get_rhel_version(),
        help="change the rhel version of the " + "environment, default is " +
             get_rhel_version() + " (from your system)")

    return parser


def main():

    # e = environment()

    parser = make_parser()
    args = parser.parse_args()

    module = args.module_name

    # if args.epics_version:
    #     if not args.epics_version.startswith("R"):
    #         args.epics_version = "R%s" % args.epics_version
    #     if e.epics_ver_re.match(args.epics_version):
    #         e.setEpics(args.epics_version)
    #     else:
    #         parser.error("Expected epics version like R3.14.8.2, got: " +
    #                      args.epics_version)

    if args.area == "ioc":
        assert len(module.split('/')) > 1, 'Missing Technical Area under Beamline'

    # Force options.svn if no releases in the file system
    if args.area in ["etc", "tools", "epics"]:
        args.git = True

    # Check for the existence of releases of this module/IOC    
    release_paths = []    
    if args.git:
        # source = os.path.join(path.prodArea(args.area), module)
        import path_functions
        source = os.path.join(path_functions.devModule(args.module_name, args.area))
        if vcs_git.is_repo_path(source):
            if os.path.isdir('./' + module):
                repo = vcs_git.git.Repo(module)
                releases = vcs_git.list_module_releases(repo)
                for release in releases:
                    print(release)
            else:
                print("Module does not exists locally")
            # if not repo (repo = clone(), clone = true)
            # release_paths.append(tag in repo.tags)
            # if clone (shutil(repo))
    # else:
    #     prodArea = e.prodArea(args.area)
    #     if args.area == 'python' and args.rhel_version >= 6:
    #         prodArea = os.path.join(prodArea, "RHEL%s-%s" %
    #                                 (args.rhel_version, platform.machine()))
    #     release_dir = os.path.join(prodArea, module)
    #
    #     if os.path.isdir(release_dir):
    #         for p in os.listdir(release_dir):
    #             if os.path.isdir(os.path.join(release_dir, p)):
    #                 release_paths.append(p)

    # check some releases have been made
    if len(releases) == 0:
        if args.git:
            msg = "No releases made in git"
        else:
            msg = "No releases made for %s" % args.epics_version
        print(module + ": " + msg)
        return 1

    # sort the releases        
    # release_paths = e.sortReleases(release_paths)

    if args.latest:
        print(release_paths[-1].split("/")[-1])
    else:
        for path in release_paths:
            print(path.split("/")[-1])

if __name__ == "__main__":
    sys.exit(main())
