#!/bin/env dls-python
# This script comes from the dls_scripts python module

import os
import sys
from dls_ade.argument_parser import ArgParser
from dls_environment import git_functions as gitf

usage = """Default <area> is 'support'.

This script is used to determine the last tag of <module> which was imported into
$SVN_ROOT/diamond/vendor/support/<module>/current. This tag should be used as
the <old> parameter in the input arguments to "dls-vendor-update.py"."""


def main():

    parser = ArgParser(usage)
    parser.add_argument(
        "module_name", type=str, default="", help="name of module to checkout")
    args = parser.parse_args()

#    if len(args) != 1: >>> argparse can't run if args not given <<<
#        parser.error("Incorrect number of arguments.")
    module = args.module
    
    # import svn client
    from dls_environment.svn import svnClient
    svn = svnClient()

    if args.area == "ioc":
        assert len(module.split('/')) > 1, 'Missing Technical Area under Beamline'

    vendor = gitf.vendorModule(module, args.area)
    vendor_current = os.path.join(vendor, "current")
    svn.setLogMessage('Searching vendor module branch for last import to "current"')

    for node in svn.ls(vendor):
        tt = os.path.join(vendor, os.path.basename(node['name']))

        if os.path.basename(node['name']) != "current":
            diffs = svn.diff('/tmp', vendor_current,
                             svn.Revision(svn.opt_revision_kind.head),
                             tt, svn.Revision(svn.opt_revision_kind.head),
                             True, True, True)
            if not diffs:
                print os.path.basename(node['name'])
                break

if __name__ == "__main__":
    sys.exit(main())
