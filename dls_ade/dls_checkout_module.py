#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
import vcs_git
from argument_parser import ArgParser
import path_functions as path
from pkg_resources import require
require('GitPython')
from git import Repo as Git

usage = """%prog [options] [<module_name>]

Default <area> is 'support'.
Checkout a module in the <area> area of the repository to the current directory.
If you enter "everything" as <module_name>, the whole <area> area will be checked out."""


def make_parser():
    # parse options
    parser = ArgParser(usage)

    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")
    parser.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                        help="Checkout from a branch rather than from the trunk")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="force the checkout, disable warnings")
    return parser


def check_parsed_arguments_valid(args, parser):

    if 'module_name' not in args:
        parser.error("Module name required")


def check_technical_area(args, parser):
    module = args['module_name']

    if args['area'] == "ioc" and module != "everything" and not len(module.split('/')) > 1:
        parser.error("Missing Technical Area under Beamline")


def check_source_file_path_valid(source, parser):

    if not vcs_git.in_repo(source):
        parser.error("Repository does not contain the '" + source + "' module")


def check_module_file_path_valid(module, parser):

    if os.path.isdir(module):
        parser.error("Path already exists: " + module)


def main():

    parser = make_parser()
    args = parser.parse_args()

    if args.module_name == "everything":
        answer = raw_input("Would you like to checkout the whole " + args.area +
                           " area? This may take some time. Enter Y or N: ")
        if answer.upper() != "Y":
            return

    check_technical_area(vars(args), parser)

    module = args.module_name

    if args.branch:
        if module == "everything":
            source = path.branchArea(args.area)
            module = source.split("/")[-1]
        else:
            source = os.path.join(path.branchModule(module, args.area),
                                  args.branch)
    else:
        if module == "everything":
            source = path.devArea(args.area)
            module = source.split("/")[-1]
        else:
            source = path.devModule(module, args.area)

    check_source_file_path_valid(source, parser)
    check_module_file_path_valid(module, parser)

    # Checkout
    print 'Checking out: ' + source + '...'
    Git.clone_from(source, module)


if __name__ == "__main__":
    sys.exit(main())
