#!/bin/env dls-python
# This script comes from the dls_scripts python module

import sys
import shutil
from dls_ade.argument_parser import ArgParser
from dls_ade import path_functions as pathf
from dls_ade import vcs_git

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


def main():

    parser = make_parser()
    args = parser.parse_args()

    pathf.check_technical_area(args.area, args.module_name)

    source = pathf.dev_module_path(args.module_name, args.area)

    if not vcs_git.is_server_repo(source):
        raise Exception(args.module_name + " does not exist on repo")

    print("Branches of " + args.module_name + ":\n")

    repo = vcs_git.temp_clone(source)

    branches = vcs_git.list_remote_branches(repo)
    for branch in branches:
        print branch
    print("")

    shutil.rmtree(repo.working_tree_dir)


if __name__ == "__main__":
    sys.exit(main())
