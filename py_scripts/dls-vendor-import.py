#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <source> <module> <version>

Default <area> is 'support'.
This script is used to import, to the repository, a module given to Diamond by a vendor. 
The script imports the code from <source> to a vendor module in svn at diamond/vendor/<area>/<module>/<version>.
It also copies the code to the trunk and then checks the code out into the current directory."""

import os, sys

def vendor_import():
    from dls_scripts.options import OptionParser
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args)!=3:
        parser.error("Incorrect number of arguments.")
    
    # setup the environment
    source = args[0]
    module = args[1]
    version = args[2]
    from dls_scripts.svn import svnClient
    svn = svnClient()
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
    vendor = svn.vendorModule(module,options.area)
    vendor_current = os.path.join(vendor,"current")
    vendor_version = os.path.join(vendor,version)
    trunk = svn.devModule(module,options.area)
    disk_dir = module.split("/")[-1]
    svn.setLogMessage('Importing vendor source from: '+source)

    # Check for existence of this module in release, vendor and trunk in the repository
    check_dirs = [trunk,vendor,svn.prodModule(module,options.area)]
    for dir in check_dirs:
        assert not svn.pathcheck(dir), dir + " already exists in the repository"
    assert os.path.isdir(source), source + " does not exist"
    assert not os.path.isdir(disk_dir), disk_dir + ' exists on disk. Choose a different name or move elsewhere'

    print 'Importing vendor source from: '+source
    svn.import_(source, vendor_current,'Import of '+module+' from pristine '+version+' source',True)

    print 'Tagging vendor source at version: '+version
    svn.copy(vendor_current,vendor_version)
    
    # make directory tree if needed
    svn.mkdir(trunk[:trunk.rfind("/")])
    print 'Copying vendor source to trunk...'
    svn.copy(vendor_current,trunk)
    print 'Checking out trunk...'
    svn.checkout(trunk,disk_dir)

    print ''
    print 'Please now:'
    print '(1) Edit configure/RELEASE to put in correct paths'
    print '(2) Use make to check that it builds'
    print '(3) Commit with the following comment:'
    print '"'+module+': changed configure/RELEASE to reflect Diamond paths"'
    print ''

if __name__ == "__main__":
    sys.exit(vendor_import())
