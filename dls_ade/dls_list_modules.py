#!/bin/env dls-python
# This script comes from the dls_scripts python module

from __future__ import print_function
import sys
from argument_parser import ArgParser
import path_functions as path
import vcs_git

usage = """
Default <area> is 'support'.
List all modules in a particular <area>.
If <dom_name> and <area> = 'ioc', list the subdirectories of <dom_name>. 
e.g. %prog -p prints: converter, cothread, dls_nsga, etc.
"""


def print_module_list(source, area):
    """
    Prints the modules in the area of the repository specified by source

    Args:
        source: Suffix of URL to list from
        area: Area of repository to list

    """
    split_list = vcs_git.get_repository_list()
    print("Modules in " + area + ":\n")
    for module_path in split_list:
        if module_path.startswith(source):
            # Split module path by slashes twice and print what remains after that, i.e. after 'controls/<area>/'
            print(module_path.split('/', 2)[-1])


def make_parser():
    """
    Takes default parser arguments and adds domain.

    Returns:
        ArgParser instance
    """
    parser = ArgParser(usage)
    parser.add_argument("-d", "--domain", action="store",
                        type=str, dest="domain_name",
                        help="domain of ioc to list")
    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()
    
    if args.area == "ioc" and args.domain_name:
        source = path.devModule(args.domain_name, args.area)
    else:
        source = path.devArea(args.area)

    print_module_list(source, args.area)


if __name__ == "__main__":
    sys.exit(main())
