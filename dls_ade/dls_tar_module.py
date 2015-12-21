#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_environment import environment
from dls_ade.argument_parser import ArgParser
from dls_ade import dlsbuild
# >>> dlsbuild doesn't run because it doesnt' know what ldap is, ldap required for this?

e = environment()

usage = """
Default <area> is 'support'.
This script removes all O.* directories from an old release of a module and
tars it up before deleting the release directory. <module_name>/<module_release>
will be stored as <module_name>/<module_release>.tar.gz. Running the script with
a -u flag will untar the module and remove the archive.
"""


def make_parser():

    parser = ArgParser(usage)
    parser.add_argument(
        "module_name", type=str, default=None,
        help="name of module to tar")
    parser.add_argument(
        "release", type=str, default=None,
        help="release number of module to tar")
    parser.add_argument(
        "-u", "--untar", action="store_true", dest="untar",
        help="Untar archive created with dls-archive-module.py")
    parser.add_argument(
        "-e", "--epics_version", action="store", type=str, dest="epics_version",
        help="change the epics version, default is " + e.epicsVer() + " (from your environment)")

    return parser


def check_area(args, parser):
    if args.area not in ["support", "ioc", "python", "matlab"]:
        parser.error("Modules in area " + args.area + " cannot be archived")


def set_up_epics_environment(args, parser):

    if args.epics_version:
        if e.epics_ver_re.match(args.epics_version):
            e.setEpics(args.epics_version)
        else:
            parser.error("Expected epics version like R3.14.8.2, got: " +
                         args.epics_version)


def check_technical_area(args, parser):
    if args.area == 'ioc' and len(args.module_name.split('/')) < 2:
            parser.error("Missing Technical Area under Beamline")


def check_file_paths(release_dir, archive, args, parser):
    if args.untar:
        if not os.path.isfile(archive):
            parser.error("Archive '{0}' doesn't exist".format(archive))
        if os.path.isdir(release_dir):
            parser.error("Path '{0}' already exists".format(release_dir))
    else:
        if not os.path.isdir(release_dir):
            parser.error("Path '{0}' doesn't exist".format(release_dir))
        if os.path.isfile(archive):
            parser.error("Archive '{0}' already exists".format(archive))


def main():

    parser = make_parser()
    args = parser.parse_args()
    check_area(args, parser)
    set_up_epics_environment(args, parser)

    check_technical_area(args, parser)
    
    # Check for the existence of release of this module/IOC    
    w_dir = os.path.join(e.prodArea(args.area), args.module_name)
    release_dir = os.path.join(w_dir, args.release)
    archive = release_dir + ".tar.gz"
    check_file_paths(release_dir, archive, args, parser)
    
    # Create build object for release
    build = dlsbuild.archive_build(args.untar)
    
    if args.epics_version:
        if not args.epics_version.startswith("R"):
            args.epics_version = "R" + args.epics_version
        build.set_epics(args.epics_version)
    
    build.set_area(args.area)

    build.submit("", args.module_name, args.release)


if __name__ == "__main__":
    sys.exit(main())
