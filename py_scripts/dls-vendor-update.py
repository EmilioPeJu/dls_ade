#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <source> <module> <old> <new>

Default <area> is 'support'.

This script is used to update a vendor <module> from tag <old> to tag <new> using the code from <source>.
The updated vendor module is imported into: $SVN_ROOT/diamond/vendor/support/<module>/current" which 
contains a history of all the releases made by the vendor. The code is then copied into:
$SVN_ROOT/diamond/vendor/support/<module>/<new>.

<old> MUST be the tag used for the previous import into "current" i.e. it would have been <new>, the
last time this script was run. This is probably impossible to remember if there has been a long time span
since the last import. To determine <old>, run: dls-get-vendor-current.py.

An example of how this is run for streamDevice:

dls-vendor-update.py /home/ajf67/streamDevice/2-4 streamDevice StreamDevice-2-snapshot20080731 2-4

(Here, the "StreamDevice" directory, as packaged by the SLS, can be found immediately under:
"/home/ajf67/streamDevice/2-4". The level of directory specified as <source> will vary for other vendor 
module updates depending on the layout of the vendor module).

In this example, the previous import was of "StreamDevice-2-snapshot20080731". We are now updating to the 2-4
release. Any value other than "StreamDevice-2-snapshot20080731" for <old> would have caused this 
command to fail.

Note: It is very important to follow the instructions, given as output at the end of the script and shown below, 
for this example, asking you to merge the changes between the previous tag, <old>, and the latest tag, <new>, into 
the trunk:

svn checkout $SVN_ROOT/diamond/trunk/support/streamDevice streamDevice   (checkout the trunk).
svn merge $SVN_ROOT/diamond/vendor/support/streamDevice/StreamDevice-2-snapshot20080731 $SVN_ROOT/diamond/vendor/support/streamDevice/2-4 streamDevice

(merge the code from the previous import, with the code from the current import, into your working copy of the trunk.
This takes into account any local Diamond changes already in trunk).
Now check for conflicts and resolve these before commiting the changes back to the repository.
Finally, it is possible to make a release of the new vendor code by using "dls-release.py"."""

import os, sys
from dls_scripts.svn import svnClient
from dls_scripts.options import OptionParser

def vendor_update():
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args)!=4:
        parser.error("Incorrect number of arguments.")
    
    # setup the environment
    source = args[0]
    module = args[1]
    old = args[2]
    new = args[3]
    svn = svnClient()
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
    vendor = svn.vendorModule(module,options.area)
    vendor_old = os.path.join(vendor,old)
    vendor_new = os.path.join(vendor,new)
    vendor_current = os.path.join(vendor,"current")
    trunk = svn.devModule(module,options.area)
    disk_dir = module.split("/")[-1]
    svn.setLogMessage('Importing vendor source from: '+source)
    

    # The directory tree we are importing from must not contain any
    # .svn directories, otherwise "dls-svn_load_dirs" will fail with
    # a non-obvious error.
    found = 0
    for path, subdirs, files in os.walk(args[0]):
        for tt in subdirs:
            assert tt!='.svn', 'An .svn directory has been found in '+source+', cannot update from here!' 

    # Check for existence of this module in vendor and trunk in the repository
    for dir in [vendor,trunk,vendor_old]:
        assert svn.pathcheck(dir), dir + " does not exist in the repository"
    assert not svn.pathcheck(vendor_new), vendor_new  + " already exists in the repository"

    # check for diffs
    diffs = svn.diff( '/tmp/svn',vendor_current,svn.Revision(svn.opt_revision_kind.head),
                      vendor_old,svn.Revision(svn.opt_revision_kind.head),True, True, True)
    assert not diffs, 'Vendor "current" of: '+vendor+' is not at revision: ' + old

    print 'Importing: '+module+' from: '+source+' to update from version: '+old+' to version: '+new
    os.system('dls-svn-load-dirs.pl -t '+new+" "+vendor+" current "+source)

    print
    print 'You probably now want to merge this update into the trunk.'
    print 'Do this by issuing the following commands:'
    print
    print 'svn checkout ' + trunk + ' ' + disk_dir + ' > /dev/null'
    print 'svn merge ' + vendor_old + ' ' + vendor_new + ' ' + disk_dir
    print

if __name__ == "__main__":
    sys.exit(vendor_update())
