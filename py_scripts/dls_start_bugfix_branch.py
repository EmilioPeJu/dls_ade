#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_ade.argument_parser import ArgParser
from dls_environment import git_functions as gitf

usage = """%prog [options] <module_name> <release> <branch_name>

Default <area> is 'support'.
Start a new bug fix branch, used when a release has been made and we need to patch that release.
The script copies the release of <module_name>/<release> into a new branch <branch_name>, and is checked out in the current directory."""


def make_parser():

    parser = ArgParser(usage)

    parser.add_argument(
        "module_name", type=str, default=None,
        help="name of module to branch")
    parser.add_argument(
        "release", type=str, default=None,
        help="release number of module to branch")
    parser.add_argument(
        "branch_name", type=str, default=None,
        help="name of new module branch")

    return parser


def main():

    parser = make_parser()
    args = parser.parse_args()

#    if len(args)!=3:
#        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args.module_name
    release_number = args.release
    branch_name = args.branch_name
    
    # import svn client
    from dls_environment.svn import svnClient    
    svn = svnClient()
    svn.setLogMessage(module + ": creating bugfix branch " + branch_name)
    
    # setup area
    if args.area == "ioc":
        assert len(module.split('/')) > 1, "Missing Technical Area under Beamline"
    release = os.path.join(gitf.prodModule(module, args.area), release_number)
    branch = os.path.join(gitf.branchModule(module, args.area), branch_name)

    # Check for existence of release in svn, non-existence of branch in svn and current directory
    assert svn.pathcheck(release), 'Repository does not contain "' + release + '"'
    assert not svn.pathcheck(branch), 'Repository already contains "' + branch + '"'
    assert not os.path.isdir(branch.split("/")[-1]), \
        branch.split("/")[-1] + " already exists in this directory. " \
                                "Please choose another name or move elsewhere."

    # Make the module in branch directory if it doesn't exist
    if not svn.pathcheck(gitf.branchModule(module, args.area)):
        svn.mkdir(gitf.branchModule(module, args.area))

    svn.copy(release, branch)
    print 'Created bugfix branch from ' + module + ': ' + \
          release_number + " in " + branch
    
    svn.checkout(branch, branch_name)
    print 'Checked out to ./' + branch_name

if __name__ == "__main__":
    sys.exit(main())
