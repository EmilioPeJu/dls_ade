#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_ade import vcs_git
from dls_ade.argument_parser import ArgParser
from dls_environment import git_functions as gitf
from pkg_resources import require
require('GitPython')
from git import Repo as Git

usage = """%prog [options] [<module_name>]

Default <area> is 'support'.
Checkout a module in the <area> area of the repository to the current directory.
If you enter "everything" as module name, the whole <area> area will be checked out."""


def make_parser():
    # parse options
    parser = ArgParser(usage)

    parser.add_argument("module_name", type=str, default="",
                        help="name of module to checkout")
    parser.add_argument("-b", "--branch", action="store", type=str, dest="branch",
                        help="Checkout from a branch rather than from the trunk")
    parser.add_argument("-f", "--force", action="store_true", dest="force",
                        help="force the checkout, disable warnings")
    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()
    
    # flag = False

    if args.module_name == "everything":
        answer = raw_input("Would you like to checkout the whole " + args.area +
                           " area? This may take some time. Enter Y or N: ")
        if answer.upper() != "Y":
            return

    module = args.module_name

    if args.area == "ioc" and module != "everything":
        assert len(module.split('/')) > 1, 'Missing Technical Area under Beamline'

    if args.branch:
        if module == "everything":
            source = gitf.branchArea(args.area)
            module = source.split("/")[-1]
        else:
            source = os.path.join(gitf.branchModule(module, args.area),
                                  args.branch)
    else:
        if module == "everything":
            source = gitf.devArea(args.area)
            module = source.split("/")[-1]
        else:
            source = gitf.devModule(module, args.area)

    from dls_environment.svn import svnClient
    svn = svnClient()

    # Check for existence of this module in various places in the repository
    # assert svn.pathcheck(source), 'Repository does not contain the "' + source + \
    #                              '" module'
    assert vcs_git.in_repo(args.area, args.module_name), "Repository does not contain the '" + source + \
                                                            "' module"
    assert not os.path.isdir(module), "Path already exists: " + module

    # Checkout
    print 'Checking out: ' + source + '...'
    # svn.checkout(source, module)
    Git.clone_from(source, module)


if __name__ == "__main__":
    sys.exit(main())
