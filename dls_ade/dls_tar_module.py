#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
import vcs_git
from dls_environment import environment
from dls_ade.argument_parser import ArgParser
from dls_ade import dlsbuild

e = environment()

usage = """
Default <area> is 'support'.
This script removes all O.* directories from an old release of a module and
tars it up before deleting the release directory. <module_name>/<module_release>
will be stored as <module_name>/<module_release>.tar.gz. Running the script with
a -u flag will untar the module and remove the archive.
"""


def make_parser():
    """
    Takes default parser and adds arguments for module_name, release, -u: untar and -e: epics_version

    Returns:
        Parser: An argument parser instance with the relevant arguments
    """

    parser = ArgParser(usage)
    parser.add_argument(
        "module_name", type=str, default=None,
        help="Name of module to tar")
    parser.add_argument(
        "release", type=str, default=None,
        help="Release number of module to tar")
    parser.add_argument(
        "-u", "--untar", action="store_true", dest="untar",
        help="Untar archive created with dls-archive-module.py")
    parser.add_argument(
        "-e", "--epics_version", action="store", type=str, dest="epics_version",
        help="Change the epics version, default is " + e.epicsVer() + " (from your environment)")

    return parser


def check_area_archivable(area):
    """
    Checks parsed area is a valid option and returns a parser error if not

    Args:
        area: Area to check

    Raises:
        ValueError: "Modules in area <args.area> cannot be archived"
    """
    if area not in ["support", "ioc", "python", "matlab"]:
        raise ValueError("Modules in area " + area + " cannot be archived")


# TODO: Implement via dls_environment (also in list-releases)
def check_epics_version(epics_version):
    """
    Checks if epics version is provided. If it is, checks that it starts with 'R' and if not appends an 'R'.
    Then checks if the epics version matches the reg ex. Then sets environment epics version.

    Args:
        epics_version: Epics version to check

    Raises:
        ValueError: Expected epics version like R3.14.12.3, got: <epics_version>
    """
    if epics_version:
        if not epics_version.startswith("R"):
            epics_version = "R{0}".format(epics_version)
        if e.epics_ver_re.match(epics_version):
            e.setEpics(epics_version)
        else:
            raise ValueError("Expected epics version like R3.14.12.3, got: " + epics_version)


# TODO: Route through path_functions (also in list-releases)
def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that the technical area is also provided.

    Args:
        area: Area of repository
        module: Module to check

    Raises:
        ValueError: "Missing Technical Area under Beamline"
    """

    if area == "ioc" \
            and len(module.split('/')) < 2:
        raise ValueError("Missing Technical Area under Beamline")


def check_file_paths(release_dir, archive, untar):
    """
    Checks if the file to untar exists and the directory to build it a does not (if untar is True), or
    checks if the opposite is true (if untar is False)

    Args:
        release_dir (str): Directory to build to or to tar from
        archive (str): File to build from or to tar into
        untar (bool): True if building, False if archiving

    Raises:
        IOError: Source does not exist or target already exists
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


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_area_archivable(args.area)
    check_epics_version(args.epics_version)
    check_technical_area(args.area, args.module_name)
    
    # Check for the existence of release of this module/IOC    
    w_dir = os.path.join(e.prodArea(args.area), args.module_name)
    release_dir = os.path.join(w_dir, args.release)
    archive = release_dir + ".tar.gz"
    check_file_paths(release_dir, archive, args.untar)
    
    # Create build object for release
    build = dlsbuild.ArchiveBuild(args.untar)
    
    if args.epics_version:
        build.set_epics(args.epics_version)
    
    build.set_area(args.area)

    git = vcs_git.Git(args.module_name, args)
    git.set_version(args.release)

    build.submit(git)


if __name__ == "__main__":
    sys.exit(main())
