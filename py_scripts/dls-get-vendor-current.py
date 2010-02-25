#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module>

Default <area> is 'support'.

This script is used to determine the last tag of <module> which was imported into
$SVN_ROOT/diamond/vendor/support/<module>/current. This tag should be used as
the <old> parameter in the input arguments to "dls-vendor-update.py"."""

import os, sys
from dls_scripts.svn import svnClient
from dls_scripts.options import OptionParser

def get_vendor_current():
    parser = OptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args[0]
    svn    = svnClient()

    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'

    vendor = svn.vendorModule(module,options.area)
    vendor_current = os.path.join(vendor,"current")
    svn.setLogMessage('Searching vendor module branch for last import to "current"')

    for node in svn.ls(vendor):
      tt = os.path.join(vendor,os.path.basename(node['name']))

      if os.path.basename(node['name']) != "current":
        diffs = svn.diff( '/tmp/svn',vendor_current,svn.Revision(svn.opt_revision_kind.head),
                           tt,svn.Revision(svn.opt_revision_kind.head),True, True, True)
        if not diffs:
          print os.path.basename(node['name'])
          break

if __name__ == "__main__":
    sys.exit(get_vendor_current())
