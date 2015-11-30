#!/bin/env dls-python
# This script comes from the dls_scripts python module

import sys
from argument_parser import ArgParser
from dls_environment import environment
import path_functions as path

usage = """Default <area> is 'support'.
Check if a module in the <area> area of the repository has had changes committed since its last release."""


def make_parser():
    # parse options
    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str,
                        help="name of module to release")
    return parser


def check_parsed_arguments_valid(args, parser):

    if 'module_name' not in args:
        parser.error("Module name required")


def check_technical_area_valid(args, parser):
    module = args['module']
    area = args['area']

    if area == "ioc" and not len(module.split('/')) > 1:
        parser.error("Missing Technical Area Under Beamline")


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_parsed_arguments_valid(vars(args), parser)
    check_technical_area_valid(vars(args), parser)

    # setup the environment
    e = environment()

    module = args.module_name

    source = path.devModule(module, args.area)
    release = path.prodModule(module, args.area)
                
    # Check for existence of this module in various places in the repository and note revisions
    assert svn.pathcheck(source), "Repository does not contain '" + source + "'"

    last_trunk_rev = svn.info2(source, recurse=False)[0][1]["last_changed_rev"].number

    if svn.pathcheck(release):
        last_release_rev = \
            svn.info2(release, recurse=False)[0][1]["last_changed_rev"].number
        last_release_num = \
            e.sortReleases([x["name"] for x in svn.ls(release)])[-1].split("/")[-1]
        # print the output
        if last_trunk_rev > last_release_rev:
            print(module + " (" + last_release_num + \
                  "): Outstanding changes. Release = r" + \
                  str(last_release_rev) + ", Trunk = r" + \
                  str(last_trunk_rev))
        else:
            print(module + " (" + last_release_num + "): Up to date.")
    else:
        print(module + " (No release done): Outstanding changes.")
    

if __name__ == "__main__":
    sys.exit(main())
