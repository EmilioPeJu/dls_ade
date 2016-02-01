#!/bin/env dls-python
# This script comes from the dls_scripts python module
# new branch
"""
Clone a module, an ioc domain or an entire area of the repository.
When cloning a single module, the branch argument will automatically checkout the given branch.
"""

import os
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
        An ArgumentParser instance

    """
    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")
    parser.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                        help="Checkout a specific named branch rather than the default (master)")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="force the checkout, disable warnings")
    return parser


def check_technical_area(area, module):
    """
    Checks if given area is IOC and if so, checks that the module name
    is of the format <domain>/<module> or is not given

    Args:
        area: Area of repository
        module: Name of module

    Raises:
        Exception: Missing technical area under beamline

    """
    if area == "ioc" \
            and module != "everything" \
            and len(module.split('/')) < 2:
        raise Exception("Missing Technical Area under Beamline")


def check_source_file_path_valid(source):
    """
    Checks if given source path exists on the repository

    Args:
        source: Path to module to be cloned

    Raises:
        Exception: Repository does not contain <source>

    """
    if not vcs_git.is_server_repo(source):
        raise Exception("Repository does not contain " + source)


def check_module_file_path_valid(module):
    """
    Checks if the given module already exists in the current directory

    Args:
        module: Name of module to clone

    Raises:
        Exception: Path already exists: <module>

    """
    if os.path.isdir(module):
        raise Exception("Path already exists: " + module)


def main():

    parser = make_parser()
    args = parser.parse_args()

    if args.module_name == "everything":
        answer = raw_input("Would you like to checkout the whole " +
                           args.area + " area? This may take some time. Enter Y or N: ")
        if answer.upper() != "Y":
            return

    check_technical_area(args.area, args.module_name)

    module = args.module_name

    if module == "everything":
        # Set source to area folder
        source = pathf.dev_area_path(args.area)
    else:
        # Set source to module in area folder
        source = pathf.dev_module_path(module, args.area)

    if module == "everything":
        print("Checking out entire " + args.area + " area...\n")
        vcs_git.clone_multi(source)
    else:
        print("Checking out " + module + " from " + args.area + " area...")
        check_module_file_path_valid(module)
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
