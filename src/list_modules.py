#!/bin/env python2.4

author = "Tom Cobb"
usage = """%prog [options] [<dom_name>]

Default <area> is 'support'.
List all modules in a particular area <area>.
If <dom_name> and <area> = 'ioc', list the subdirectories of <dom_name>. 
e.g. %prog -i BL18I prints MO,VA,DI,etc. """

import os, sys
from common import *

@doc(usage)
def list_modules():    
    parser = svnOptionParser(usage)
    (options, args) = parser.parse_args()
    if len(args) not in [0,1]:
        parser.error("Incorrect number of arguments.")
    
    # setup the environment
    svn = svnClient()
    if options.area=="ioc" and len(args)==1:
        source = svn.devModule(args[0],options.area)
    else:
        source = svn.devArea(options.area)

    # print the modules
    assert svn.pathcheck(source), source + " does not exist in the repository"
    for node in svn.ls(source):
        print os.path.basename(node['name'])

if __name__ == "__main__":
    list_modules()
