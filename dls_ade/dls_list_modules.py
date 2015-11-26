#!/bin/env dls-python
# This script comes from the dls_scripts python module

from __future__ import print_function
import sys
import subprocess
from argument_parser import ArgParser
import path_functions as path
import vcs_git

usage = """
Default <area> is 'support'.
List all modules in a particular area <area>.
If <dom_name> and <area> = 'ioc', list the subdirectories of <dom_name>. 
e.g. %prog -i BL18I prints MO,VA,DI,etc. """


def check_source_file_path_valid(source, parser):

    if not vcs_git.is_repo_path(source):
        parser.error("Repository does not contain " + source)


def print_module_list(source):

    list_cmd = "ssh " + vcs_git.GIT_ROOT + " expand controls"
    split_list = subprocess.check_output(list_cmd.split()).split()
    for path in split_list:
        if source in path:
            print(path)


def main():

    parser = ArgParser(usage)
    parser.add_argument("-d", "--domain", action="store",
                        type=str, dest="domain_name",
                        help="domain of ioc to list")

    args = parser.parse_args()
    
    if args.area == "ioc" and args.domain_name:
        source = path.devModule(args.domain_name, args.area)
    else:
        source = path.devArea(args.area)

    check_source_file_path_valid(source, parser)

    print_module_list(source)

if __name__ == "__main__":
    sys.exit(main())
