#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_ade.argument_parser import ArgParser
from dls_environment import git_functions as gitf

usage = """%prog [options] [<dom_name>]

Default <area> is 'support'.
List all modules in a particular area <area>.
If <dom_name> and <area> = 'ioc', list the subdirectories of <dom_name>. 
e.g. %prog -i BL18I prints MO,VA,DI,etc. """


def main():

    parser = ArgParser(usage)
    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")

    args = parser.parse_args()

    if len(args) not in [0, 1]:
        parser.error("Incorrect number of arguments.")
    
    # import svn client
    from dls_environment.svn import svnClient    
    svn = svnClient()
    import pysvn
    
    if args.area == "ioc" and len(args) == 1:
        source = gitf.devModule(args.module, args.area)
    else:
        source = gitf.devArea(args.area)

    assert svn.pathcheck(source), source + " does not exist in the repository"

    # print the modules
    for node, _ in svn.list(source, depth=pysvn.depth.immediates)[1:]:
        print os.path.basename(node.path)


if __name__ == "__main__":
    sys.exit(main())
