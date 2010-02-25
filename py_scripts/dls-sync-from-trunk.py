#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog

Synchronise a working copy of a branch with the changes from the trunk.
No changes will be committed to the repository, the only changes made will be to the working copy."""

import os, sys, shutil
from dls_scripts.options import OptionParser
from dls_scripts.svn import svnClient

def sync_from_trunk():
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args)!=0:
        parser.error("Incorrect number of arguments.")
    
    # setup the environment
    svn = svnClient()

    # Check that we are currently in a working copy of a branch
    isWC = svn.workingCopy()
    assert isWC and "branches" in isWC.url, 'You must run this script in a working copy of a feature branch'
    branch = isWC.url[:isWC.url.rfind("/")]
    trunk = branch.replace("branches","trunk")
    prop_list = svn.propget('dls:synced-from-trunk','.',svn.Revision(svn.opt_revision_kind.working),False)
    assert prop_list, 'The "dls:synced-from-trunk" property is not set for this branch'
    merge_from = prop_list['']
    assert merge_from, 'Merge revision information not available'
    print 'merging from version = ' + merge_from + ' to HEAD'
    svn.merge(trunk, svn.Revision(svn.opt_revision_kind.number, merge_from),
              trunk, svn.Revision(svn.opt_revision_kind.head), '.', True, True)

    # Checkout the latest version of the module from the trunk to find out the new number of HEAD
    tempdir = os.path.join('/tmp/svn/sync_from_trunk')
    if os.path.isdir(tempdir):
        shutil.rmtree(tempdir)
    svn.checkout(trunk,tempdir)
    trunk_revision = svn.info(tempdir).revision.number
    shutil.rmtree(tempdir)

    # Update the "dls:synced-from-trunk" property which tells us how far up the trunk we have merged into this branch.
    print 'Set new HEAD version number in branch = ', trunk_revision
    svn.propset('dls:synced-from-trunk',str(trunk_revision),'.',svn.Revision(svn.opt_revision_kind.working),False)

if __name__ == "__main__":
    sys.exit(sync_from_trunk())
