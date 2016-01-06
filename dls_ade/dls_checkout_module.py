#!/bin/env dls-python
# This script comes from the dls_scripts python module
# new branch
import os
import sys
from dls_ade import vcs_git
from dls_ade.argument_parser import ArgParser
from dls_ade import path_functions as path

usage = """
Default <area> is 'support'.
Checkout a module in the <area> area of the repository to the current directory.
If you enter "everything" as <module_name>, the whole <area> area will be checked out.
"""


def make_parser():
    """
    Creates default parser and adds module_name, --branch and --force arguments

    Args:

    Returns:
        An ArgumentParser instance with relevant arguments
    """
    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")
    parser.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                        help="Checkout a specific named branch rather than the default (master)")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="force the checkout, disable warnings")
    return parser


def check_technical_area(args, parser):
    """
    Checks if given area is IOC and if so, checks that either 'everything' is given as the module name
    or that the technical area is also provided

    Args:
        args(dict): Parser arguments
        parser(ArgumentParser): Parser instance

    Raises:
        error: Missing Technical Area under Beamline
    """
    if args.area == "ioc" \
            and args.module_name != "everything" \
            and len(args.module_name.split('/')) < 2:
        parser.error("Missing Technical Area under Beamline")


def check_source_file_path_valid(source, parser):
    """
    Checks if given source path exists on the repository

    Args:
        source(str): Path to module to be cloned
        parser(ArgumentParser): Parser instance

    Raises:
        error: Repository does not contain <source>
    """
    if not vcs_git.is_repo_path(source):
        parser.error()


def check_module_file_path_valid(module, parser):
    """
    Checks if the given module already exists in the current directory

    Args:
        module(str): Name of module to clone
        parser(ArgumentParser): Parser instance

    Raises:
        error: Path already exists: <module>
    """
    if os.path.isdir(module):
        parser.error("Path already exists: " + module)


def main():

    parser = make_parser()
    args = parser.parse_args()

    if args.module_name == "everything":
        answer = raw_input("Would you like to checkout the whole " +
                           args.area + " area? This may take some time. Enter Y or N: ")
        if answer.upper() != "Y":
            return

    check_technical_area(args, parser)

    module = args.module_name

    if module == "everything":
        # Set source to area folder
        source = path.devArea(args.area)
    else:
        # Set source to module in area folder
        source = path.devModule(module, args.area)

    if module == "everything":
        print("Checking out entire " + args.area + " area...\n")
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
