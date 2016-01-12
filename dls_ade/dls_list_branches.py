#!/bin/env dls-python
# This script comes from the dls_scripts python module

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
    """
    Takes default parser arguments and adds domain.

    Returns:
        Parser with relevant arguments
    """

    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")
    return parser


def check_technical_area(args, parser):
    """
    Checks if given area is IOC and if so, checks that either 'everything' is given as the module
    name or that the technical area is also provided. Raises parser error if not.

    Args:
        args: Parser arguments
        parser: Parser

    Raises:
        error: Missing Technical Area under Beamline
    """

    if args.area == "ioc" and len(args.module_name.split('/')) < 2:
        parser.error("Missing Technical Area under Beamline")


def main():

    parser = make_parser()
    args = parser.parse_args()

    check_technical_area(args, parser)

    source = path.devModule(args.module_name, args.area)

    if not vcs_git.is_repo_path(source):
        parser.error(args.module_name + " does not exist on repo")

    print("Branches of " + args.module_name + ":\n")

    repo = vcs_git.temp_clone(source)

    branches = vcs_git.list_remote_branches(repo)
    for branch in branches:
        print branch
    print("")

    shutil.rmtree(repo.working_tree_dir)


if __name__ == "__main__":
    sys.exit(main())
