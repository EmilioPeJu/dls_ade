#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_ade.argument_parser import ArgParser
from dls_environment import git_functions as gitf


usage = """%prog [options] <module_name>

Default <area> is 'support'.
List the branches of a module in the <area> area of the repository."""


def main():

    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")

    args = parser.parse_args()

#    if len(args) != 1:
#        parser.error("Incorrect number of arguments.")

    module = args.module_name
    
    # import svn client
    from dls_environment.svn import svnClient    
    svn = svnClient()

    if args.area == "ioc":
        assert len(module.split('/')) > 1, 'Missing Technical Area under Beamline'

    source = gitf.devModule(module, args.area)
    branch = gitf.branchModule(module, args.area)

    # Check for existence of this module/IOC in "trunk" in the repository
    assert svn.pathcheck(source), source + " does not exist in the repository"
    assert svn.pathcheck(branch), branch + " does not exist in the repository"

    for node in svn.ls(branch):
        print os.path.basename(node['name'])

if __name__ == "__main__":
    sys.exit(main())
