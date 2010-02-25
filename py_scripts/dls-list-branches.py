#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name>

Default <area> is 'support'.
List the branches of a module in the <area> area of the repository."""

import os, sys

def list_branches():    
    from dls_scripts.options import OptionParser
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("Incorrect number of arguments.")
    module = args[0]
    
    # import svn client
    from dls_scripts.svn import svnClient    
    svn = svnClient()

    if options.area=="ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
    source = svn.devModule(module,options.area)
    branch = svn.branchModule(module,options.area)

    # Check for existence of this module/IOC in "trunk" in the repository
    assert svn.pathcheck(source), source + " does not exist in the repository"
    assert svn.pathcheck(branch), branch + " does not exist in the repository"
    for node in svn.ls(branch):
        print os.path.basename(node['name'])

if __name__ == "__main__":
    sys.exit(list_branches())
