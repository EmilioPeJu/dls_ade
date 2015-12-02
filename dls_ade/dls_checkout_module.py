#!/bin/env dls-python
# This script comes from the dls_scripts python module
# new branch
import os
import sys
import vcs_git
from argument_parser import ArgParser
import path_functions as path

usage = """Default <area> is 'support'.
Checkout a module in the <area> area of the repository to the current directory.
If you enter "everything" as <module_name>, the whole <area> area will be checked out."""


def make_parser():

    parser = ArgParser(usage)

    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")
    parser.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                        help="Checkout a branch rather than master")
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

    if not vcs_git.is_repo_path(source):
        parser.error("Repository does not contain " + source)


def check_module_file_path_valid(module, parser):

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

    check_technical_area(vars(args), parser)

    module = args.module_name

    if module == "everything":
        source = path.devArea(args.area)
    else:
        source = path.devModule(module, args.area)

    if module == "everything":
        print("Checking out " + source + " area...\n")
        vcs_git.clone_multi(source, module)
    else:
        print("Checking out " + module + " from " + source + "...\n")
        vcs_git.clone(source, module)

    if args.branch:
        os.chdir(args.module_name)
        branches = vcs_git.list_branches()
        if args.branch in branches:
            vcs_git.checkout_branch(args.branch)
        else:
            print("Branch '" + args.branch + "' does not exist in " + source +
                  "\nBranch List:\n")
            for entry in branches:
                print(entry)
            print("\nWhich branch would you like to checkout?")
            branch = raw_input("Enter branch: ")
            if branch in branches and branch != "master":
                vcs_git.checkout_branch(branch)
            else:
                print("\nmaster branch checked out by default")


if __name__ == "__main__":
    sys.exit(main())
