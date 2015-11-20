#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_ade.argument_parser import ArgParser
from dls_environment import git_functions as gitf

usage = """%prog [options] <source> <module> <version>

Default <area> is 'support'.
This script is used to import, to the repository, a module given to Diamond by a vendor. 
The script imports the code from <source> to a vendor module in svn at diamond/vendor/<area>/<module>/<version>.
It also copies the code to the trunk and then checks the code out into the current directory."""


def make_parser():
    parser = ArgParser(usage)

    parser.add_argument(
        "source", type=str, default=None,
        help="name of module to release")
    parser.add_argument(
        "module_name", type=str, default=None,
        help="name of module to release")
    parser.add_argument(
        "release", type=str, default=None,
        help="release number of module to release")

    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()

#    if len(args)!=3:
#        parser.error("Incorrect number of arguments.")
    
    # setup the environment
    source = args.source
    module = args.module_name
    version = args.release

    if args.area == "ioc":
        assert len(module.split('/')) > 1, "Missing Technical Area under Beamline"
    vendor = gitf.vendorModule(module, args.area)
    vendor_current = os.path.join(vendor, "current")
    vendor_version = os.path.join(vendor, version)
    trunk = gitf.devModule(module, args.area)
    disk_dir = module.split("/")[-1]
    svn.setLogMessage("Importing vendor source from: " + source)

    # Check for existence of this module in release, vendor and trunk in the repository
    check_dirs = [trunk, vendor, gitf.prodModule(module, args.area)]
    for dir in check_dirs:
        assert not svn.pathcheck(dir), dir + " already exists in the repository"
    assert os.path.isdir(source), source + " does not exist"
    assert not os.path.isdir(disk_dir), \
        disk_dir + " exists on disk. Choose a different name or move elsewhere"

    print("Importing vendor source from: " + source)
    svn.import_(source, vendor_current, "Import of " + module + " from pristine " + version +
                " source", True)

    print("Tagging vendor source at version: " + version)
    svn.copy(vendor_current, vendor_version)
    
    # make directory tree if needed
    svn.mkdir(trunk[:trunk.rfind("/")])
    print("Copying vendor source to trunk...")
    svn.copy(vendor_current, trunk)
    print("Checking out trunk...")
    svn.checkout(trunk, disk_dir)

    print("")
    print("Please now:")
    print("(1) Edit configure/RELEASE to put in correct paths")
    print("(2) Use make to check that it builds")
    print("(3) Commit with the following comment:")
    print("\"' + module + ': changed configure/RELEASE to reflect Diamond paths\"")
    print("")

if __name__ == "__main__":
    sys.exit(main())
