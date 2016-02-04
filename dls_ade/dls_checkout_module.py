#!/bin/env dls-python
# This script comes from the dls_scripts python module
"""
Clone a module, an ioc domain or an entire area of the repository.
When cloning a single module, the branch argument will automatically checkout the given branch.
"""

import sys
from dls_ade import vcs_git
from dls_ade.argument_parser import ArgParser
from dls_ade import path_functions as pathf

usage = """
Default <area> is 'support'.
Checkout a module from the <area> area of the repository to the current directory.
If you enter no <module_name>, the whole <area> area will be checked out.
"""


def make_parser():
    """
    Takes ArgParse instance with default arguments and adds

    Positional Arguments:
        * module_name

    Flags:
        * -b (branch)

    Returns:
        :class:`argparse.ArgumentParser`:  ArgParse instance
    """
    parser = ArgParser(usage)
    parser.add_branch_flag(
        help_msg="Checkout a specific named branch rather than the default (master)")

    parser.add_argument("module_name", nargs="?", type=str, default="",
                        help="Name of module")

    return parser


def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that the module name
    is of the format <domain>/<module> or is not given.

    Args:
        area(str): Area of repository
        module(str): Name of module

    Raises:
        Exception: Missing technical area under beamline

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
        source = pathf.dev_area_path(args.area)
    else:
        # Set source to module in area folder
        source = pathf.dev_module_path(module, args.area)

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
