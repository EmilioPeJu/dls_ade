#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name> <release> <branch_name>

Default <area> is 'support'.
Start a new bug fix branch, used when a release has been made and we need to patch that release.
The script copies the release of <module_name>/<release> into a new branch <branch_name>, and is checked out in the current directory."""

import os, sys
from dls_scripts.options import OptionParser
from dls_scripts.svn import svnClient

def start_bugfix_branch():
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args)!=3:
        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args[0]
    release_number = args[1]
    branch_name = args[2]
    svn = svnClient()
    svn.setLogMessage(module + ": creating bugfix branch "+branch_name)
    
    # setup area
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
    release = os.path.join(svn.prodModule(module,options.area),release_number)
    branch = os.path.join(svn.branchModule(module,options.area),branch_name)

    # Check for existence of release in svn, non-existence of branch in svn and current directory
    assert svn.pathcheck(release), 'Repository does not contain "'+release+'"'
    assert not svn.pathcheck(branch), 'Repository already contains "'+branch+'"'
    assert not os.path.isdir(branch.split("/")[-1]), branch.split("/")[-1]+" already exists in this directory. Please choose another name or move elsewhere."

    # Make the module in branch directory if it doesn't exist
    if not svn.pathcheck(svn.branchModule(module,options.area)):
        svn.mkdir(svn.branchModule(module,options.area))

    svn.copy(release,branch)
    print 'Created bugfix branch from '+module+': '+ release_number + " in "+branch
    
    svn.checkout(branch,branch_name)
    print 'Checked out to ./'+branch_name

if __name__ == "__main__":
    sys.exit(start_bugfix_branch())
