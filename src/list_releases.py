#!/bin/env python2.4

author = "Tom Cobb"
usage = """%prog [options] <module_name>

Default <area> is 'support'.
List the releases of a module in area <area>.
"""

import os, sys
from common import *

@doc(usage)
def list_releases():    
    from dls.environment import environment
    parser = svnOptionParser(usage)
    parser.add_option("-l", "--latest", action="store_true", dest="latest", help="Only print the latest release")
    (options, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args[0]
    svn = svnClient()
    e = environment()
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
    source = svn.devModule(module,options.area)
    releases = svn.prodModule(module,options.area)
    
    # Check for the existence of releases of this module/IOC
    assert svn.pathcheck(source), source + " does not exist in the repository"
    assert svn.pathcheck(releases), releases + " does not exist in the repository"
    release_paths = e.sortReleases([node["name"] for node in svn.ls(releases)])
    if options.latest:
        print release_paths[-1].split("/")[-1]
    else:
        for path in release_paths:
            print path.split("/")[-1]

if __name__ == "__main__":
    from pkg_resources import require
    require("dls.environment==1.0")
    list_releases()
