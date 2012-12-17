#!/bin/env dls-python2.6
# This script comes from the dls_scripts python module

usage = """%prog [options] [<module_name>]

Default <area> is 'support'.
Checkout a module in the <area> area of the repository to the current directory.
If you do not enter a module name, the whole <area> area will be checked out."""

import os, sys

def checkout_module():
    from dls_environment.options import OptionParser
    parser = OptionParser(usage)
    parser.add_option("-b", "--branch", action="store", type="string", dest="branch",help="Checkout from a branch rather than from the trunk")
    parser.add_option("-f", "--force", action="store_true", dest="force", help="force the checkout, disable warnings")
    (options, args) = parser.parse_args()
    
    flag = False
    if len(args)==0:
        a=raw_input("Would you like to checkout the whole "+options.area+" area? This may take some time. Enter Y or N: ")
        if a.upper() == "N":
            return
        else:
            module = ""
    else:
        if len(args)!=1:
            parser.error("Incorrect number of arguments.")
        module = args[0]
    
    # import svn client
    from dls_environment.svn import svnClient    
    svn = svnClient()

    if options.area == "ioc" and module!="":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'

    if options.branch:
        if module=="":
            source = svn.branchArea(options.area)
            module = source.split("/")[-1]
        else:
            source = os.path.join(svn.branchModule(module,options.area),options.branch)
    else:
        if module=="":
            source = svn.devArea(options.area)
            module = source.split("/")[-1]
        else:
            source = svn.devModule(module,options.area)

    # Check for existence of this module in various places in the repository
    assert svn.pathcheck(source),'Repository does not contain the "'+source+'" module'
    assert not os.path.isdir(module),'Path already exists: '+module

    # Checkout
    print 'Checking out: '+source+'...'
    svn.checkout(source,module)
    
if __name__ == "__main__":
    sys.exit(checkout_module())
