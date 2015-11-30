#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_environment import environment
from dls_ade.argument_parser import ArgParser
from dls_ade import dlsbuild
# >>> dlsbuild doesn't run because it doesnt' know what ldap is, ldap required for this?

usage = """Default <area> is 'support'.
This script removes all O.* directories from an old release of a module and
tars it up before deleting the release directory. <module_name>/<module_release>
will be stored as <module_name>/<module_release>.tar.gz. Running the script with
a -u flag will untar the module and remove the archive.
"""


def make_parser():
    e = environment()

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


def main():

    e = environment()

    parser = make_parser()
    args = parser.parse_args()

#    if len(args) != 2:
#        parser.error("Incorrect number of arguments.")

    module = args.module_name
    release = args.release

    if args.untar:
        action = "unarchive"
    else:
        action = "archive"

    assert args.area in ("support", "ioc", "python", "matlab"), \
        "Modules in area ' " + args.area + "' cannot be archived"

    # setup the environment
    if args.epics_version:
        if e.epics_ver_re.match(args.epics_version):
            e.setEpics(args.epics_version)
        else:
            parser.error("Expected epics version like R3.14.8.2, got: " + args.epics_version)
    if args.area == "ioc":
        assert len(module.split('/')) > 1, "Missing Technical Area under Beamline"
    
    # Check for the existence of release of this module/IOC    
    w_dir = os.path.join(e.prodArea(args.area), module)
    
    # If an archive already exists fail
    release_dir = os.path.join(w_dir, release)
    archive = release_dir + ".tar.gz"

    if args.untar:
        assert os.path.isfile(archive), "Archive '%s' doesn't exist" % archive
        assert not os.path.isdir(release_dir), "Path '%s' already exists" % release_dir        
    else:
        assert os.path.isdir(release_dir), "Path '%s' doesn't exist" % release_dir
        assert not os.path.isfile(archive), "Archive '%s' already exists" % archive
    
    # Create build object for release
    build = dlsbuild.archive_build(args.untar)
    
    if args.epics_version:
        if not args.epics_version.startswith("R"):
            args.epics_version = "R" + args.epics_version
        build.set_epics(args.epics_version)
    
    build.set_area(args.area)

    build.submit("", module, release)


if __name__ == "__main__":
    sys.exit(main())
