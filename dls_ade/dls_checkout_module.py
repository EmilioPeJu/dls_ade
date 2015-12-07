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
    Takes default parser arguments and adds module_name, --branch and --force.

    :return: Parser with relevant arguments
    :rtype: ArgumentParser
    """
    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")
    parser.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                        help="Checkout a branch rather than master")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="force the checkout, disable warnings")
    return parser


def check_parsed_arguments_valid(args, parser):
    """
    Checks if module_name has been provided and raises a parser error if not.

    :param args: Parser arguments
    :type args: dict
    :param parser: Parser
    :type parser: ArgumentParser
    :return: Null
    """
    if 'module_name' not in args:
        parser.error("Module name required")


def check_technical_area(args, parser):
    """
    Checks if given area is IOC and if so, checks that either 'everything' is given as the module name
    or that the technical area is also provided. Raises parser error if not.

    :param args: Parser arguments
    :type args: dict
    :param parser: Parser
    :type parser: ArgumentParser
    :return: Null
    """
    if args['area'] == "ioc" \
            and args['module_name'] != "everything" \
            and len(args['module_name'].split('/')) < 2:
        parser.error("Missing Technical Area under Beamline")


def check_source_file_path_valid(source, parser):
    """
    Checks if given source path exists on the repository and raises a parser error if it does not.

    :param source: Path to module to be cloned
    :type source: str
    :param parser: Parser
    :type parser: ArgumentParser
    :return: Null
    """
    if not vcs_git.is_repo_path(source):
        parser.error("Repository does not contain " + source)


def check_module_file_path_valid(module, parser):
    """
    Checks if the given module already exists in the current directory. Raises error if so.

    :param module: Name of module to clone
    :type module: str
    :param parser: Parser
    :type parser: ArgumentParser
    :return: Null
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

    check_technical_area(vars(args), parser)

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
        vcs_git.clone(source, module)

    if args.branch:
        # cd into new module and get remote branches
        os.chdir(args.module_name)
        branches = vcs_git.list_remote_branches()
        if args.branch in branches:
            vcs_git.checkout_remote_branch(args.branch)
        else:
            # Invalid branch name, print branches and ask user to re-enter the branch they want
            print("Branch '" + args.branch + "' does not exist in " + source +
                  "\nBranch List:\n")
            for entry in branches:
                print(entry)
            print("\nWhich branch would you like to checkout?")
            branch = raw_input("Enter branch: ")
            if branch in branches and branch != "master":
                vcs_git.checkout_remote_branch(branch)
            else:
                print("\nmaster branch checked out by default")


if __name__ == "__main__":
    sys.exit(main())
