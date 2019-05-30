#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
List the releases that have been made for a module in prod or on the repository.
Default epics version and rhel version are the set from you environment,
to specify different versions the epics version or rhel version flags can be used.
The git flag will list releases from the repository.
"""

import os
import sys
import shutil
import json
import platform
import logging

from dls_ade.dls_environment import environment
from dls_ade.argument_parser import ArgParser
from dls_ade.dls_utilities import check_technical_area
from dls_ade import vcs_git, Server
from dls_ade import logconfig

usage = """
Default <area> is 'support'.

List the releases of <module_name> in the <area> area of prod or the repository 
if -g is true. By default uses the epics release number from your environment 
to work out the area on disk to look for the module, this can be overridden 
with the -e flag.
"""


def get_rhel_version():
    """
    Checks if platform is Linux redhat, if so returns base version number from
    environment (e.g. returns 6 if 6.7), if not returns default of 6.

    Returns:
        str: Rhel version number
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
    Takes ArgParse instance with default arguments and adds

    Positional Arguments:
        * module_name

    Flags:
        * -b (branch)
        * -l (latest)
        * -g (git)
        * -e (epics_version)
        * -r (rhel_version)

    Returns:
        :class:`argparse.ArgumentParser`:  ArgParse instance
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


def _main():
    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger(name="usermessages")
    output = logging.getLogger(name="output")

    parser = make_parser()
    args = parser.parse_args()

    env = environment()

    log.info(json.dumps({'CLI': sys.argv, 'options_args': vars(args)}))

    env.check_epics_version(args.epics_version)
    env.check_rhel_version(str(args.rhel_version))
    check_technical_area(args.area, args.module_name)

    # Force check of repo, not file system, for tools, etc and epics
    # (previous releases are only stored on repo)
    if args.area in ["etc", "tools", "epics"]:
        args.git = True

    # Check for the existence of releases of this module/IOC
    releases = []
    if args.git:

        server = Server()

        # List branches of repository
        target = "the repository"
        source = server.dev_module_path(args.module_name, args.area)
        log.debug(source)

        vcs = server.temp_clone(source)
        releases = vcs_git.list_module_releases(vcs.repo)
        shutil.rmtree(vcs.repo.working_tree_dir)

    else:
        # List branches from prod
        target = "prod for {os}".format(os=env.rhelVerDir())
        source = env.prodArea(args.area)
        release_dir = os.path.join(source, args.module_name)

        if os.path.isdir(release_dir):
            for p in os.listdir(release_dir):
                if os.path.isdir(os.path.join(release_dir, p)):
                    releases.append(p)

    # Check some releases have been made
    if len(releases) == 0:
        if args.git:
            usermsg.info("{}: No releases made in git".format(args.module_name))
        else:
            usermsg.info("{module}: No releases made for {version}".format(
                module=args.module_name,
                version=args.epics_version
            ))
        return 1

    releases = env.sortReleases(releases)

    if args.latest:
        usermsg.info("The latest release for {module} in {target} is: "
                     .format(module=args.module_name, target=target))
        output.info("{release}".format(release=releases[-1]))
    else:
        usermsg.info("Previous releases for {module} in {target}:"
                     .format(module=args.module_name, target=target))
        output.info("{releases}".format(releases=str(releases)))


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-list-releases.py')
        _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception(
            "ABORT: Unhandled exception (see trace below): {}".format(e)
        )
        exit(1)


if __name__ == "__main__":
    main()
