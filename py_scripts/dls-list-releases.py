#!/bin/env dls-python
# This script comes from the dls_scripts python module

usage = """%prog [options] <module_name>

Default <area> is 'support'.
List the releases of a module in area <area>.
"""

import os, sys
from dls_scripts.options import OptionParser
from dls_environment import environment

def list_releases():
    e = environment()    
    parser = OptionParser(usage)
    parser.add_option("-l", "--latest", action="store_true", dest="latest", help="Only print the latest release")
    parser.add_option("-e", "--epics_version", action="store", type="string", dest="epics_version", help="change the epics version, default is "+e.epicsVer()+" (from your environment)")
    (options, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("Incorrect number of arguments.")

    # setup the environment
    module = args[0]
    if options.epics_version:
        if e.epics_ver_re.match(options.epics_version):
            e.setEpics(options.epics_version)
        else:
            parser.error("Expected epics version like R3.14.8.2, got: "+options.epics_version)
    if options.area == "ioc":
        assert len(module.split('/'))>1, 'Missing Technical Area under Beamline'
            
    # Check for the existence of releases of this module/IOC    
    release_dir = os.path.join(e.prodArea(options.area), module)
    if not os.path.isdir(release_dir):
    	print module + ": No releases made"
    	return 1

	# sort the releases        
    release_paths = e.sortReleases(os.listdir(release_dir))
    if options.latest:
        print release_paths[-1].split("/")[-1]
    else:
        for path in release_paths:
            print path.split("/")[-1]

if __name__ == "__main__":
    sys.exit(list_releases())
