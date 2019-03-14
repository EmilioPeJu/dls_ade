#!/bin/env dls-python
# This script comes from the dls_scripts python module

"""
This script removes all O.* directories from a release of a module and tars it
up before deleting the release directory.
<module_name>/<module_release> will be stored as
<module_name>/<module_release>.tar.gz. Running the script with the -u flag will
untar the module and remove the archive (reversing the original process)
"""

import os
import sys
import json
import logging

from dls_ade import vcs_git
from dls_ade.dls_environment import environment
from dls_ade.argument_parser import ArgParser
from dls_ade import dlsbuild
from dls_ade.dls_utilities import check_technical_area
from dls_ade import logconfig

env = environment()

usage = """
Default <area> is 'support'.
This script removes all O.* directories from a release of a module and
tars it up before deleting the release directory. <module_name>/<module_release>
will be stored as <module_name>/<module_release>.tar.gz. Running the script with
a -u flag will untar the module and remove the archive (reversing the original process)
"""


def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Positional Arguments:
        * module_name
        * release

    Flags:
        * -u: `untar`
        * -e: `epics_version`

    Returns:
        :class:`argparse.ArgumentParser`: ArgParse instance

    """

    parser = ArgParser(usage)
    parser.add_module_name_arg()
    parser.add_release_arg()
    parser.add_epics_version_flag()
    parser.add_rhel_version_flag()

    parser.add_argument(
        "-u", "--untar", action="store_true", dest="untar",
        help="Untar archive created with dls-archive-module.py")

    return parser


def check_area_archivable(area):
    """
    Checks parsed area is a valid option and returns a parser error if not

    Args:
        area(str): Area to check

    Raises:
        :class:`exceptions.ValueError`: Modules in area <args.area> cannot be
            archived

    """
    if area not in ["support", "ioc", "python", "matlab"]:
        raise ValueError("Modules in area " + area + " cannot be archived")


def check_file_paths(release_dir, archive, untar):
    """
    Checks if the file to untar exists and the directory to build it a does not
    (if `untar` is True), or checks if the opposite is true
    (if `untar` is False)

    Args:
        release_dir(str): Directory to build to or to tar from
        archive(str): File to build from or to tar into
        untar(bool): True if building, False if archiving

    Raises:
        IOError:
            * `untar` true and archive doesn't exist:
                Archive <archive> doesn't exist
            * `untar` true and path already exists:
                Path <release_dir> already exists
            * `untar` false and archive already exists:
                Archive <archive> doesn't exist
            * `untar` false and path doesn't exist:
                Path <release_dir> already exists

    """
    if untar:
        if not os.path.isfile(archive):
            raise IOError("Archive '{0}' doesn't exist".format(archive))
        if os.path.isdir(release_dir):
            raise IOError("Path '{0}' already exists".format(release_dir))
    else:
        if not os.path.isdir(release_dir):
            raise IOError("Path '{0}' doesn't exist".format(release_dir))
        if os.path.isfile(archive):
            raise IOError("Archive '{0}' already exists".format(archive))


def _main():
    log = logging.getLogger(name="dls_ade")
    usermsg = logging.getLogger("usermessages")

    parser = make_parser()
    args = parser.parse_args()

    log.info(json.dumps({'CLI': sys.argv, 'options_args': vars(args)}))

    check_area_archivable(args.area)
    env.check_epics_version(args.epics_version)
    env.check_rhel_version(args.rhel_version)
    check_technical_area(args.area, args.module_name)
    
    # Check for the existence of release of this module/IOC    
    w_dir = os.path.join(env.prodArea(args.area), args.module_name)
    release_dir = os.path.join(w_dir, args.release)
    archive = release_dir + ".tar.gz"

    check_file_paths(release_dir, archive, args.untar)
    
    # Create build object for release
    build = dlsbuild.ArchiveBuild(args.rhel_version, args.epics_version, args.untar)
    
    if args.epics_version:
        build.set_epics(args.epics_version)
    
    build.set_area(args.area)

    git = vcs_git.Git(args.module_name, args.area)
    git.set_version(args.release)

    build.submit(git)


def main():
    # Catch unhandled exceptions and ensure they're logged
    try:
        logconfig.setup_logging(application='dls-tar-module.py')
        return _main()
    except Exception as e:
        logging.exception(e)
        logging.getLogger("usermessages").exception("ABORT: Unhandled exception (see trace below): {}".format(e))
        exit(1)


if __name__ == "__main__":
    sys.exit(main())
