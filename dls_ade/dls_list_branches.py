#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
import shutil
from argument_parser import ArgParser
import path_functions as path
import vcs_git

usage = """
Default <area> is 'support'.
List the branches of a module in the <area> area of the repository.
"""


def make_parser():
    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")
    return parser


def check_technical_area(args, parser):
    if args['area'] == "ioc" and len(args['module_name'].split('/')) < 2:
        parser.error("Missing Technical Area under Beamline")


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_technical_area(vars(args), parser)

    module = args.module_name
    source = path.devModule(module, args.area)

    if not vcs_git.is_repo_path(source):
        parser.error("Module does not exist on repo")

    if not os.path.isdir('./' + module):
        print("Cloning module " + module + " to current directory...\n")
        vcs_git.clone(source, module)
        cloned = True
    else:
        print("Module " + module + " already exists in the current directory\n")
        cloned = False

    os.chdir(module)

    branches = vcs_git.list_remote_branches()
    print("Branches of " + module + ":\n")
    for branch in branches:
        print branch
    print("")

    os.chdir('..')

    if cloned:
        shutil.rmtree(module)

if __name__ == "__main__":
    sys.exit(main())
