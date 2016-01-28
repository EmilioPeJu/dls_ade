#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_ade import vcs_git
from dls_ade.argument_parser import ArgParser
from dls_ade import path_functions as path

usage = """
Default <area> is 'support'.
Checkout a module in the <area> area of the repository to the current directory.
If you enter no <module_name>, the whole <area> area will be checked out.
"""


def make_parser():
    """
    Creates default parser and adds module_name, --branch and --force arguments

    Args:

    Returns:
        An ArgumentParser instance with relevant arguments
    """
    parser = ArgParser(usage)
    parser.add_argument("module_name", nargs="?", type=str, default="",
                        help="name of module to checkout")
    parser.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                        help="Checkout a specific named branch rather than the default (master)")
    return parser


def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that either 'everything' is given as the module name
    or that the technical area is also provided

    Args:
        area(str): Area of repository
        module(str): Name of module

    Raises:
        Exception: "Missing Technical Area under Beamline"
    """
    if area == "ioc" and module != "" and len(module.split('/')) < 2:
        raise Exception("Missing Technical Area under Beamline")


def main():

    parser = make_parser()
    args = parser.parse_args()

    if args.module_name == "":
        answer = raw_input("Would you like to checkout the whole " +
                           args.area + " area? This may take some time. Enter Y or N: ")
        if answer.upper() != "Y":
            return

    check_technical_area(args.area, args.module_name)

    module = args.module_name

    if module == "":
        # Set source to area folder
        source = path.devArea(args.area)
    else:
        # Set source to module in area folder
        source = path.devModule(module, args.area)

    if module == "":
        print("Checking out entire " + args.area + " area...\n")
        vcs_git.clone_multi(source)
    elif module.endswith('/') and args.area == 'ioc':
        print("Checking out " + module + " technical area...")
        vcs_git.clone_multi(source)
    else:
        print("Checking out " + module + " from " + args.area + " area...")
        repo = vcs_git.clone(source, module)

        if args.branch:
            # Get branches list
            branches = vcs_git.list_remote_branches(repo)
            if args.branch in branches:
                vcs_git.checkout_remote_branch(args.branch, repo)
            else:
                # Invalid branch name, print branches list and exit
                print("Branch '" + args.branch + "' does not exist in " + source +
                      "\nBranch List:\n")
                for entry in branches:
                    print(entry)


if __name__ == "__main__":
    sys.exit(main())
