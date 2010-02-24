#!/bin/env python2.4

author = "Tom Cobb"
usage = """%prog [options] <module_name>

Default <area> is 'support'.
Check if a module in the <area> area of the repository has had changes committed since its last release."""

import os, sys
from common import *

@doc(usage)
def changes_since_release():
    from dls.environment import environment
    parser = svnOptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("Incorrect number of arguments.")
    
    # setup the environment
    e = environment()
    module = args[0]
    svn = svnClient()
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
    source = svn.devModule(module,options.area)
    release = svn.prodModule(module,options.area)
                
    # Check for existence of this module in various places in the repository and note revisions
    assert svn.pathcheck(source), 'Repository does not contain "'+source+'"'
    last_trunk_rev = svn.info2(source,recurse=False)[0][1]["last_changed_rev"].number
    assert svn.pathcheck(release), 'Repository does not contain "'+release+'"'
    last_release_rev = svn.info2(release,recurse=False)[0][1]["last_changed_rev"].number
    last_release_num = e.sortReleases([x["name"] for x in svn.ls(release)])[-1].split("/")[-1]
    
    # print the output
    if last_trunk_rev > last_release_rev:
        print module+" ("+last_release_num+"): Outstanding changes. Release = r"+str(last_release_rev)+", Trunk = r"+str(last_trunk_rev) 
    else:
        print module+" ("+last_release_num+"): Up to date." 

if __name__ == "__main__":
    from pkg_resources import require
    require("dls.environment==1.0")
    changes_since_release()
